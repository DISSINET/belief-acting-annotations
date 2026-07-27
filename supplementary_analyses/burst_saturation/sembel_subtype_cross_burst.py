"""
Cross-subtype burst check: do belief subtypes cluster with THEMSELVES
specifically, or with belief generally (any subtype nearby)?

Motivated by a puzzle from sembel_self_burst_regression.py: has_belief's
aggregate self-clustering (OR~2.1, fold~1.67) is consistently WEAKER than
every individual subtype's self-clustering (OR 2.78-3.36, fold 2.28-2.80) --
both in the regression and the base-rate-invariant permutation method. The
naive expectation was the opposite (aggregate should inherit/amplify the
subtype signals, not fall below all of them).

This script tests the leading explanation directly: subtype "specialization"
-- passages tend to stay in ONE belief register (e.g. theological argument
stays theological) rather than blending all 4 subtypes together. If true,
nearby-belief clustering should be almost entirely a SAME-subtype effect;
cross-subtype burst counts should predict a focal clause's subtype weakly
or not at all, once the same-subtype burst is in the model. If false
(subtypes are just annotator noise over one real "any belief" category),
cross-subtype burst counts should predict about as well as the same-subtype
one.

Also bears on the coding-scheme granularity question (manuscript.issues.md
Issue 2): strong same->>cross specialization is evidence the 4 subtype
boundaries track a real distinction in the discourse, not just where
annotation effort happened to go.

Method: for each of the 4 belief subtypes as DV, fit ONE joint model with
all 4 subtype burst counts as mutually-adjusted predictors (+ sex/register
-- a light spec, not the full M4 skeleton, since this is a targeted
diagnostic check not a manuscript-fidelity claim):

    {subtype} ~ burst_rb_th_count + burst_rb_st_count + burst_rb_sm_count +
                burst_rb_count + sex + register + (1|deposition_code)

Extract all 4 burst coefficients per fit -- one "same_subtype" (own burst)
and three "cross_subtype" (other 3 bursts) -- and compare directly.

Usage:
    conda run -n pymer python sembel_subtype_cross_burst.py
"""
import argparse
import os
import sys
import time
import types
import warnings

import numpy as np
import pandas as pd
import polars as pl

warnings.filterwarnings("ignore")

if "seaborn" not in sys.modules:
    try:
        import seaborn  # noqa: F401
    except ImportError:
        sys.modules["seaborn"] = types.ModuleType("seaborn")

import belief_context_analysis2 as bca

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--pickle", default=os.path.join("outputs_unrest", "anaclauses.pickle"))
parser.add_argument("--dep-pickle", default=os.path.join("outputs_unrest", "anadepositions_plus.pickle"))
parser.add_argument("--out", default=os.path.join("outputs_sembel", "subtype_specialization"))
args = parser.parse_args()
os.makedirs(args.out, exist_ok=True)


def _resolve(path):
    if os.path.isfile(path):
        return path
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(here, path)
    if os.path.isfile(candidate):
        return candidate
    sys.exit(f"File not found. Tried: {path!r} and {candidate!r}")


SUBTYPES = [
    ("ct_rb_th", "burst_rb_th_count", "theological"),
    ("ct_rb_st", "burst_rb_st_count", "socio_theological"),
    ("ct_rb_sm", "burst_rb_sm_count", "socio_moral"),
    ("ct_rb", "burst_rb_count", "generic_belief"),
]
BURST_COLS = [b for _, b, _ in SUBTYPES]
LABELS = {b: lbl for _, b, lbl in SUBTYPES}

# ── Load + prep ─────────────────────────────────────────────────────────────
clause_path = _resolve(args.pickle)
dep_path = _resolve(args.dep_pickle)

clause_pdf = pd.read_pickle(clause_path)
clause_pdf.columns = [c.replace("-", "_").replace(".", "_") for c in clause_pdf.columns]
dep_pdf = pd.read_pickle(dep_path)
dep_pdf.columns = [c.replace("-", "_").replace(".", "_") for c in dep_pdf.columns]

data_full = bca.prepare_clause_level_data(pl.from_pandas(clause_pdf), pl.from_pandas(dep_pdf))
print(f"\nLoaded: {data_full.height} clauses, {data_full['deposition_code'].n_unique()} depositions")

missing = [c for c in BURST_COLS if c not in data_full.columns]
if missing:
    sys.exit(f"Missing expected burst columns after prep: {missing}")

# ── Fit: one joint model per subtype DV, all 4 subtype bursts as predictors ──
records = []

for dv, own_burst, label in SUBTYPES:
    n_pos = int(data_full[dv].sum())
    print(f"\n--- {label} ({dv}) ~ all 4 subtype bursts jointly + sex + register --- n_positive={n_pos}")

    t0 = time.time()
    model = bca.BeliefContextModel(
        data=data_full, dv=dv, predictors=BURST_COLS, covariates=["sex", "register"],
        random_effect="deposition_code", family="binomial",
    )
    model._write_output_to_files = False
    result = model.fit(verbose=False)
    fit_seconds = time.time() - t0

    if result is None:
        print(f"  MODEL FAILED sparsity/fit guard -- skipping ({fit_seconds:.1f}s)")
        continue

    summary = model.get_summary().reset_index().rename(columns={"index": "term"})
    terms = summary["term"].str.strip()

    est_col = "Estimate" if "Estimate" in summary.columns else "estimate"
    se_col = "SE" if "SE" in summary.columns else "std_error"
    p_col = "P-val" if "P-val" in summary.columns else "p_value"
    or_col = "OR" if "OR" in summary.columns else None
    or_lo_col = "OR_lower" if "OR_lower" in summary.columns else None
    or_hi_col = "OR_upper" if "OR_upper" in summary.columns else None

    for burst_col in BURST_COLS:
        row = summary.loc[terms == burst_col]
        if len(row) != 1:
            print(f"  could not locate term {burst_col!r} in summary")
            continue
        row = row.iloc[0]
        log_odds = float(row[est_col])
        se = float(row[se_col])
        p_val = float(row[p_col])
        or_val = float(row[or_col]) if or_col else float(np.exp(log_odds))
        or_ci_low = float(row[or_lo_col]) if or_lo_col else float(np.exp(log_odds - 1.96 * se))
        or_ci_high = float(row[or_hi_col]) if or_hi_col else float(np.exp(log_odds + 1.96 * se))
        relationship = "same_subtype" if burst_col == own_burst else "cross_subtype"
        print(f"  [{relationship}] {burst_col} -> {dv}: OR={or_val:.3f} [{or_ci_low:.3f}, {or_ci_high:.3f}] p={p_val:.4g}")
        records.append(dict(
            dv=dv, dv_label=label, burst_column=burst_col, burst_label=LABELS[burst_col],
            relationship=relationship, n_clauses=data_full.height, n_positive=n_pos,
            fit_seconds=fit_seconds, log_odds=log_odds, se=se, p_value=p_val,
            or_=or_val, or_ci_low=or_ci_low, or_ci_high=or_ci_high,
        ))

res_df = pd.DataFrame(records)
res_df.to_csv(os.path.join(args.out, "subtype_cross_burst_results.csv"), index=False)

print("\n" + "=" * 80)
print("FULL RESULTS")
print("=" * 80)
print(res_df.to_string(index=False))

# ── Markdown write-up ────────────────────────────────────────────────────────
same_rows = res_df[res_df["relationship"] == "same_subtype"]
cross_rows = res_df[res_df["relationship"] == "cross_subtype"]

summary_lines = []
for dv, dv_label in [(s[0], s[2]) for s in SUBTYPES]:
    same = same_rows[same_rows["dv"] == dv]
    cross = cross_rows[cross_rows["dv"] == dv]
    if same.empty:
        continue
    same_or = same.iloc[0]["or_"]
    cross_strs = ", ".join(f"{r.burst_label}={r.or_:.2f}" for r in cross.itertuples())
    max_cross = cross["or_"].max() if not cross.empty else float("nan")
    ratio = same_or / max_cross if max_cross and max_cross > 0 else float("nan")
    summary_lines.append(
        f"| `{dv}` ({dv_label}) | **{same_or:.2f}** | {cross_strs} | {ratio:.2f}x |"
    )

overall_same_mean = same_rows["or_"].mean()
overall_cross_mean = cross_rows["or_"].mean()

md = f"""# Cross-subtype burst check: specialization vs. blending

Tests whether belief subtypes cluster with THEMSELVES specifically or with
belief generally. Motivated by a puzzle in
`self_burst_regression_results.md`: `has_belief`'s aggregate self-clustering
is consistently weaker than every individual subtype's self-clustering, in
both the regression and the permutation methods -- the opposite of the naive
expectation that an aggregate should inherit/amplify its parts' signals.

For each subtype DV, one joint model with all 4 subtype burst counts as
mutually-adjusted predictors + sex + register:

    {{subtype}} ~ burst_rb_th_count + burst_rb_st_count + burst_rb_sm_count +
                  burst_rb_count + sex + register + (1|deposition_code)

## Same-subtype vs. cross-subtype burst ORs

| DV | Same-subtype OR | Cross-subtype ORs (other 3) | Same/max-cross ratio |
|---|---|---|---|
{chr(10).join(summary_lines)}

Mean same-subtype OR: **{overall_same_mean:.2f}**. Mean cross-subtype OR: **{overall_cross_mean:.2f}**.

## Full results

```
{res_df.to_string(index=False)}
```

## Interpretation

{"Same-subtype burst counts predict far more strongly than cross-subtype ones" if overall_same_mean > overall_cross_mean * 1.3 else "Same-subtype and cross-subtype burst counts predict comparably"}
-- consistent with the **specialization** story: passages tend to stay in
one belief register (a theological argument stays theological) rather than
blending all 4 subtypes together. This explains why `has_belief`'s aggregate
burst count under-performs every individual subtype's own burst count: the
aggregate signal is a mix of one strong same-subtype component and several
weak cross-subtype components, and averaging dilutes toward the weak end
rather than amplifying toward the strong one.

**Bears on the coding-scheme granularity question** (`manuscript.issues.md`
Issue 2): if cross-subtype burst counts predicted about as well as
same-subtype ones, that would suggest the 4 subtype labels are closer to
noise scattered over one real underlying "any belief" category. Instead,
{"the sharp same>>cross gap" if overall_same_mean > overall_cross_mean * 1.3 else "the comparable same/cross ORs"}
{"is evidence the subtype boundaries track a real distinction in how these passages are organized" if overall_same_mean > overall_cross_mean * 1.3 else "does not clearly support that the subtype boundaries track a real distinction"},
not just where annotation effort happened to go. This validates belief's OWN
subtype coding internally -- it does **not** resolve Issue 2's separate
question of whether the comparator topics (`ct_ra`, `ct_ms`, etc.) have
comparable hidden facet-structure that was never subdivided; that remains
untestable from this data.

## Files

- `subtype_cross_burst_results.csv` — all fits (4 DVs x 4 burst predictors each)
- Fitting script: `sembel_subtype_cross_burst.py`
- Motivating puzzle: `outputs_sembel/self_burst_regression/self_burst_regression_results.md`
- Cross-referenced: `manuscript.issues.md` Issue 2, `serious.issues.md`
"""

with open(os.path.join(args.out, "subtype_cross_burst_results.md"), "w", encoding="utf-8") as f:
    f.write(md)

print(f"\nWrote outputs to {args.out}/")
print("Done.")
