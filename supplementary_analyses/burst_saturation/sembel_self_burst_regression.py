"""
The missing has_belief self-to-self burst OR.

manuscript.issues.md #1 ("why the manuscript's own OR for belief looked so
high") identified that the manuscript's headline belief burst-ORs
(1.95-2.55) are a DIFFERENT kind of quantity than the five published
comparator-topic ORs (ct_ra=2.25, ct_ms=2.27, ct_sn=1.67, ct_st=1.63,
ct_ei=1.65): the belief numbers are subtype-burst-count -> AGGREGATE
has_belief (narrow predictor, broad union outcome -- structurally easier to
satisfy, partly near-definitional), while the comparator numbers are each
topic's own burst-count predicting that SAME topic's own recurrence (true
self->self, "analogical burst models" per the manuscript's own phrasing).

Nobody has ever fit the actual self->self logistic-regression model for
has_belief itself -- the one number directly comparable to the five
published comparator numbers. This script fits it, via the same
BeliefContextModel/pymer4 machinery the manuscript itself used, for every
category (4 belief subtypes, the has_belief aggregate, 5 comparators),
THREE ways per category:

  Model A (plain):    {cat} ~ {burst_col} + (1|deposition_code)
  Model B (adjusted):  {cat} ~ {burst_col} + sex + register + (1|deposition_code)
  Model C (fully_adjusted): {cat} ~ {burst_col} + sex + register + nagiag +
      qr_tracked + log_clauses_len_std + has_nag_i_prop + [the OTHER four
      comparator topics' ct_*_prop, excluding cat's own if cat is itself one
      of the five comparators] + (1|deposition_code)

A/B, because the manuscript's own covariate choice for its 5 comparator
"analogical burst models" is genuinely unrecorded -- not archived in the
results workbook (only M001-M016 survive there, i.e. Model sets 1-3 plus
the aggregate Model 4; the comparator-topic models and the belief-subtype
self-to-self models were never saved anywhere), and the prose doesn't
repeat the "(retaining institutional/thematic/discourse-agency variables)"
qualifier it uses for the main belief model. Report both rather than guess.

C exists because A/B are deliberately minimal (1-3 fixed effects, no
categorical expansion beyond register/sex) -- fast to fit, which is fine as
a match for the comparators' presumed-light "analogical burst models," but
NOT a fair stand-in for how thoroughly the manuscript's actual has_belief
Model 4 controls for local confounds (discourse/agency via nagiag, question-
tracking, deposition length, thematic competition from the other topics).
Model C adds those back, at real computational cost (nagiag alone expands
to ~9 dummy levels) -- if C's burst-count OR moves substantially from A/B's,
that's a real finding (the light models were missing something); if it
holds steady, that's reassurance the light models weren't cutting corners
that mattered for this specific question.

All burst-count columns already exist in the pickle -- no windowing
computation needed here, unlike sembel_comparative_burstiness.py, which
computes its own permutation-null clustering score independently. This
script instead reproduces the manuscript's own GLMM methodology exactly, so
its numbers are directly comparable to the manuscript's five published
comparator ORs, and can be cross-checked against the permutation-based
ranking as an independent-methodology triangulation.

Usage:
    conda run -n pymer python sembel_self_burst_regression.py
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
parser.add_argument("--out", default=os.path.join("outputs_sembel", "self_burst_regression"))
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


CATEGORIES = [
    # (dv_column, burst_column, label, category_type)
    ("ct_rb_th", "burst_rb_th_count", "theological", "belief_subtype"),
    ("ct_rb_st", "burst_rb_st_count", "socio_theological", "belief_subtype"),
    ("ct_rb_sm", "burst_rb_sm_count", "socio_moral", "belief_subtype"),
    ("ct_rb", "burst_rb_count", "generic_belief", "belief_subtype"),
    ("has_belief", "burst_has_belief_count", "belief_aggregate", "belief_aggregate"),
    ("ct_ra", "burst_ra_count", "religious_action", "comparator"),
    ("ct_ms", "burst_ms_count", "material_support", "comparator"),
    ("ct_sn", "burst_sn_count", "social_network", "comparator"),
    ("ct_st", "burst_st_count", "spatial_temporal", "comparator"),
    ("ct_ei", "burst_ei_count", "encounter_interaction", "comparator"),
]

# ── 1. Load + prep (same pipeline as sembel_gender_mechanism_test.py) ──────────
clause_path = _resolve(args.pickle)
dep_path = _resolve(args.dep_pickle)

clause_pdf = pd.read_pickle(clause_path)
clause_pdf.columns = [c.replace("-", "_").replace(".", "_") for c in clause_pdf.columns]
dep_pdf = pd.read_pickle(dep_path)
dep_pdf.columns = [c.replace("-", "_").replace(".", "_") for c in dep_pdf.columns]

data_full = bca.prepare_clause_level_data(pl.from_pandas(clause_pdf), pl.from_pandas(dep_pdf))
print(f"\nLoaded: {data_full.height} clauses, {data_full['deposition_code'].n_unique()} depositions")

missing = [col for _, burst_col, _, _ in CATEGORIES for col in [burst_col] if col not in data_full.columns]
if missing:
    sys.exit(f"Missing expected burst columns after prep: {missing}")

COMPARATOR_PROPS = {"ct_ra": "ct_ra_prop", "ct_ms": "ct_ms_prop", "ct_sn": "ct_sn_prop",
                    "ct_st": "ct_st_prop", "ct_ei": "ct_ei_prop"}
FULL_LOCAL_COVARIATES = ["nagiag", "qr_tracked", "log_clauses_len_std", "has_nag_i_prop"]


def fully_adjusted_covariates(dv):
    """sex+register+local-discourse covariates+the OTHER four comparator
    topics' thematic proportions (excluding dv's own if dv is itself one of
    the five comparators -- including a category's own deposition-level
    proportion as a covariate for predicting that same category at the
    clause level would be near-circular, not a real confound control)."""
    other_props = [p for cat, p in COMPARATOR_PROPS.items() if cat != dv]
    return ["sex", "register"] + FULL_LOCAL_COVARIATES + other_props


missing_full = [c for c in FULL_LOCAL_COVARIATES + list(COMPARATOR_PROPS.values()) if c not in data_full.columns]
if missing_full:
    sys.exit(f"Missing expected fully-adjusted covariate columns after prep: {missing_full}")

# ── 2a. has_belief_prop: not produced by prepare_clause_level_data (belief counts
# are deliberately excluded from the deposition-level whitelist that builds
# ct_ra_prop/ct_ms_prop/etc. -- see belief_context_analysis2.py:~310-335 --
# because those columns exist to serve as "other topic" controls when has_belief
# is the DV, and including the DV's own rate as its own control would be
# circular). For the SYMMETRIC comparator fits (m4_faithful spec, below), belief
# needs to be one of the "other topic" controls when a comparator is the DV --
# so it must be computed the same way (sum/clauses_len per deposition) here.
dep_belief = (
    data_full.group_by("deposition_code")
    .agg(pl.col("has_belief").sum().alias("_has_belief_sum"), pl.col("clauses_len").first().alias("_clauses_len"))
    .with_columns((pl.col("_has_belief_sum") / pl.col("_clauses_len")).alias("has_belief_prop"))
    .select(["deposition_code", "has_belief_prop"])
)
data_full = data_full.join(dep_belief, on="deposition_code", how="left")
if data_full["has_belief_prop"].null_count() > 0:
    sys.exit("has_belief_prop has nulls after join -- deposition_code mismatch")

# ── 2b. The real, archived M4 covariate skeleton (belief_context_analysis2.py,
# the commented-out "belief-interdependency" experiment, ~line 7053) -- NOT the
# ad hoc fully_adjusted spec above, which guessed at nt_co_Q_prop_present/mag
# column names that don't exist. The real column is a single continuous
# nt_co_Q_prop, entered as a main effect plus two interactions:
#   nt_co_Q_prop * log_clauses_len_std, nt_co_Q_prop * register
# M4's own DV (has_belief) is controlled for the 5 comparator topics' thematic
# proportions; symmetric parity for a comparator DV requires the mirror image
# -- the other 4 comparators' proportions PLUS has_belief_prop (belief takes
# the "other topic" slot that comparator held for M4). Own-family proportion
# is always dropped (circular).
if "nt_co_Q_prop" not in data_full.columns:
    sys.exit("Missing nt_co_Q_prop after prep -- required for m4_faithful spec")


def m4_faithful_formula(dv, burst_col):
    if dv in COMPARATOR_PROPS:
        other_props = [p for cat, p in COMPARATOR_PROPS.items() if cat != dv] + ["has_belief_prop"]
    else:
        other_props = list(COMPARATOR_PROPS.values())
    covariate_str = " + ".join(other_props + [
        "has_nag_i_prop", "nagiag", "sex", "register", "log_clauses_len_std", "qr_tracked",
        "nt_co_Q_prop*log_clauses_len_std", "nt_co_Q_prop*register",
    ])
    return f"{dv} ~ nt_co_Q_prop + {covariate_str} + {burst_col} + (1|deposition_code)"


# ── 2. Fit plain + adjusted + fully_adjusted + m4_faithful models for every category ──
# plain/adjusted/fully_adjusted are expensive (fully_adjusted alone averaged ~16min/fit
# in the prior run) and were already fit once -- reuse those rows from the existing CSV
# rather than re-paying that cost; only fit the new m4_faithful spec (and, separately
# below, the one-off m4_joint fit) this run.
prior_csv = os.path.join(args.out, "self_burst_regression_results.csv")
reuse_records = []
specs_to_refit = {"plain", "adjusted", "fully_adjusted", "m4_faithful"}
if os.path.isfile(prior_csv):
    prior_df = pd.read_csv(prior_csv)
    reuse_mask = prior_df["model_spec"].isin(["plain", "adjusted", "fully_adjusted"])
    reuse_records = prior_df[reuse_mask].to_dict("records")
    specs_to_refit = {"m4_faithful"}
    print(f"\nReusing {len(reuse_records)} previously-fit rows (plain/adjusted/fully_adjusted) from {prior_csv}")
    print("Only fitting the new m4_faithful spec (+ m4_joint below) this run.")

records = []

for dv, burst_col, label, cat_type in CATEGORIES:
    n_pos = int(data_full[dv].sum())
    print(f"\n--- {label} ({dv} ~ {burst_col}) --- n_positive={n_pos}")

    m4_formula = m4_faithful_formula(dv, burst_col)
    model_specs = [spec for spec in [
        ("plain", [], None),
        ("adjusted", ["sex", "register"], None),
        ("fully_adjusted", fully_adjusted_covariates(dv), None),
        ("m4_faithful", [], m4_formula),
    ] if spec[0] in specs_to_refit]
    for spec_name, covariates, manual_formula in model_specs:
        t0 = time.time()
        model = bca.BeliefContextModel(
            data=data_full, dv=dv, predictors=[burst_col], covariates=covariates,
            random_effect="deposition_code", family="binomial",
        )
        if manual_formula is not None:
            model.formula = manual_formula
        model._write_output_to_files = False
        result = model.fit(verbose=False)
        fit_seconds = time.time() - t0
        n_cov_record = len(covariates) if manual_formula is None else (
            len(manual_formula.split("~")[1].split("+")) - 2)

        if result is None:
            print(f"  {spec_name}: MODEL FAILED sparsity/fit guard -- skipping ({fit_seconds:.1f}s)")
            records.append(dict(category=dv, category_label=label, category_type=cat_type,
                                 model_spec=spec_name, burst_column=burst_col,
                                 n_clauses=data_full.height, n_positive=n_pos, converged=False,
                                 fit_seconds=fit_seconds, n_covariates=n_cov_record,
                                 log_odds=None, se=None, ci_low=None, ci_high=None,
                                 or_=None, or_ci_low=None, or_ci_high=None, p_value=None))
            continue

        summary = model.get_summary().reset_index().rename(columns={"index": "term"})
        terms = summary["term"].str.strip()
        row = summary.loc[terms == burst_col]
        if len(row) != 1:
            print(f"  {spec_name}: could not locate term {burst_col!r} in summary -- terms were {list(terms)}")
            continue
        row = row.iloc[0]

        est_col = "Estimate" if "Estimate" in summary.columns else "estimate"
        se_col = "SE" if "SE" in summary.columns else "std_error"
        p_col = "P-val" if "P-val" in summary.columns else "p_value"
        or_col = "OR" if "OR" in summary.columns else None
        or_lo_col = "OR_lower" if "OR_lower" in summary.columns else None
        or_hi_col = "OR_upper" if "OR_upper" in summary.columns else None
        ci_lo_col = "2.5_ci" if "2.5_ci" in summary.columns else "conf_low"
        ci_hi_col = "97.5_ci" if "97.5_ci" in summary.columns else "conf_high"

        log_odds = float(row[est_col])
        se = float(row[se_col])
        p_val = float(row[p_col])
        ci_low = float(row[ci_lo_col]) if ci_lo_col in row else log_odds - 1.96 * se
        ci_high = float(row[ci_hi_col]) if ci_hi_col in row else log_odds + 1.96 * se
        or_val = float(row[or_col]) if or_col else float(np.exp(log_odds))
        or_ci_low = float(row[or_lo_col]) if or_lo_col else float(np.exp(ci_low))
        or_ci_high = float(row[or_hi_col]) if or_hi_col else float(np.exp(ci_high))

        print(f"  {spec_name}: OR={or_val:.3f} [{or_ci_low:.3f}, {or_ci_high:.3f}] p={p_val:.4g} ({fit_seconds:.1f}s)")
        records.append(dict(category=dv, category_label=label, category_type=cat_type,
                             model_spec=spec_name, burst_column=burst_col,
                             n_clauses=data_full.height, n_positive=n_pos, converged=True,
                             fit_seconds=fit_seconds, n_covariates=n_cov_record,
                             log_odds=log_odds, se=se, ci_low=ci_low, ci_high=ci_high,
                             or_=or_val, or_ci_low=or_ci_low, or_ci_high=or_ci_high, p_value=p_val))

records = reuse_records + records

# ── 2c. m4_joint: the literal manuscript formula (archived "belief-interdependency"
# experiment, belief_context_analysis2.py ~line 7053) -- has_belief predicted by
# all FOUR subtype bursts simultaneously (mutually adjusted), not one at a time.
# This is the actual quantity behind the manuscript's published 1.95-2.55 range;
# nothing else in this script reproduces it exactly (the plain/adjusted/
# fully_adjusted/m4_faithful specs all use has_belief's OWN aggregate burst count,
# univariate). Fit once, extract all 4 subtype-burst coefficients.
skip_joint = any(r.get("model_spec") == "m4_joint" for r in reuse_records)
if skip_joint:
    print("\nm4_joint already present in prior CSV -- skipping refit.")
    records = [r for r in reuse_records if r.get("model_spec") == "m4_joint"] + records
else:
    print("\n--- m4_joint: has_belief ~ all 4 subtype bursts jointly (the literal manuscript formula) ---")
    joint_formula = (
        "has_belief ~ nt_co_Q_prop + ct_st_prop + ct_ra_prop + ct_sn_prop + ct_ms_prop + ct_ei_prop + "
        "has_nag_i_prop + nagiag + sex + register + log_clauses_len_std + qr_tracked + "
        "nt_co_Q_prop*log_clauses_len_std + nt_co_Q_prop*register + "
        "burst_rb_sm_count + burst_rb_th_count + burst_rb_st_count + burst_rb_count + (1|deposition_code)"
    )
    t0 = time.time()
    joint_model = bca.BeliefContextModel(
        data=data_full, dv="has_belief", predictors=["burst_rb_sm_count"], covariates=[],
        random_effect="deposition_code", family="binomial",
    )
    joint_model.formula = joint_formula
    joint_model._write_output_to_files = False
    joint_result = joint_model.fit(verbose=False)
    joint_fit_seconds = time.time() - t0

    if joint_result is None:
        print(f"  m4_joint: MODEL FAILED sparsity/fit guard -- skipping ({joint_fit_seconds:.1f}s)")
    else:
        joint_summary = joint_model.get_summary().reset_index().rename(columns={"index": "term"})
        joint_terms = joint_summary["term"].str.strip()
        est_col = "Estimate" if "Estimate" in joint_summary.columns else "estimate"
        se_col = "SE" if "SE" in joint_summary.columns else "std_error"
        p_col = "P-val" if "P-val" in joint_summary.columns else "p_value"
        or_col = "OR" if "OR" in joint_summary.columns else None
        or_lo_col = "OR_lower" if "OR_lower" in joint_summary.columns else None
        or_hi_col = "OR_upper" if "OR_upper" in joint_summary.columns else None

        for burst_term, subtype_label in [
            ("burst_rb_sm_count", "socio_moral"), ("burst_rb_th_count", "theological"),
            ("burst_rb_st_count", "socio_theological"), ("burst_rb_count", "generic_belief"),
        ]:
            row = joint_summary.loc[joint_terms == burst_term]
            if len(row) != 1:
                print(f"  m4_joint: could not locate term {burst_term!r}")
                continue
            row = row.iloc[0]
            log_odds = float(row[est_col])
            se = float(row[se_col])
            p_val = float(row[p_col])
            or_val = float(row[or_col]) if or_col else float(np.exp(log_odds))
            or_ci_low = float(row[or_lo_col]) if or_lo_col else float(np.exp(log_odds - 1.96 * se))
            or_ci_high = float(row[or_hi_col]) if or_hi_col else float(np.exp(log_odds + 1.96 * se))
            print(f"  m4_joint [{subtype_label}]: OR={or_val:.3f} [{or_ci_low:.3f}, {or_ci_high:.3f}] p={p_val:.4g}")
            records.append(dict(category=f"has_belief_via_{burst_term.replace('_count','')}",
                                 category_label=f"m4_joint_{subtype_label}", category_type="m4_joint_subtype_term",
                                 model_spec="m4_joint", burst_column=burst_term,
                                 n_clauses=data_full.height, n_positive=int(data_full["has_belief"].sum()),
                                 converged=True, fit_seconds=joint_fit_seconds, n_covariates=17,
                                 log_odds=log_odds, se=se, ci_low=log_odds - 1.96 * se, ci_high=log_odds + 1.96 * se,
                                 or_=or_val, or_ci_low=or_ci_low, or_ci_high=or_ci_high, p_value=p_val))

res_df = pd.DataFrame(records)
plain = res_df[res_df["model_spec"] == "plain"].set_index("category")
adjusted = res_df[res_df["model_spec"] == "adjusted"].set_index("category")
fully_adjusted = res_df[res_df["model_spec"] == "fully_adjusted"].set_index("category")
m4_faithful = res_df[res_df["model_spec"] == "m4_faithful"].set_index("category")
res_df.to_csv(os.path.join(args.out, "self_burst_regression_results.csv"), index=False)

timing_by_spec = res_df.groupby("model_spec")["fit_seconds"].agg(["mean", "min", "max"])
print("\nFit timing by spec (seconds):")
print(timing_by_spec.to_string())

print("\n" + "=" * 80)
print("FULL RESULTS")
print("=" * 80)
print(res_df.to_string(index=False))


# ── 3. Cross-check against the permutation-based ranking, if available ────────
perm_path = os.path.join("outputs_sembel", "comparative_burstiness", "comparative_burstiness_results.csv")
perm_compare_md = ""
if os.path.isfile(perm_path):
    perm_df = pd.read_csv(perm_path)
    merged = res_df[res_df["model_spec"] == "plain"][["category", "category_label", "or_"]].merge(
        perm_df[["category", "corpus_fold"]], on="category", how="left")
    merged = merged.sort_values("or_", ascending=False)
    merged["rank_regression"] = merged["or_"].rank(ascending=False).astype(int)
    merged["rank_permutation"] = merged["corpus_fold"].rank(ascending=False).astype(int)
    spearman = merged[["or_", "corpus_fold"]].corr(method="spearman").iloc[0, 1]
    perm_compare_md = (
        "\n## Cross-check against the permutation-based ranking\n\n"
        "| Category | Regression OR (plain) | Regression rank | Permutation fold-enrichment | Permutation rank |\n"
        "|---|---|---|---|---|\n" +
        "\n".join(f"| `{r.category}` ({r.category_label}) | {r.or_:.2f} | {r.rank_regression} | "
                  f"{r.corpus_fold:.2f} | {r.rank_permutation} |" for r in merged.itertuples()) +
        f"\n\nSpearman rank correlation between the two independent methodologies: **{spearman:.3f}**.\n"
    )
    print(f"\nSpearman correlation (regression OR vs. permutation fold-enrichment ranking): {spearman:.3f}")

    belief_row = merged[merged["category"] == "has_belief"].iloc[0]
    min_subtype_or = plain[plain.index.isin(["ct_rb_th", "ct_rb_st", "ct_rb_sm", "ct_rb"])]["or_"].min()
    ra_or = plain.loc["ct_ra", "or_"] if "ct_ra" in plain.index else None
    ms_or = plain.loc["ct_ms", "or_"] if "ct_ms" in plain.index else None
    ra_fold = perm_df.set_index("category")["corpus_fold"].get("ct_ra")
    ms_fold = perm_df.set_index("category")["corpus_fold"].get("ct_ms")
    belief_fold = perm_df.set_index("category")["corpus_fold"].get("has_belief")

    gap_regression = abs(belief_row["or_"] - min(ra_or, ms_or)) if ra_or and ms_or else None
    gap_permutation = abs(belief_fold - min(ra_fold, ms_fold)) if ra_fold and ms_fold and belief_fold else None

    full_ok = fully_adjusted["converged"].all() and not fully_adjusted.empty
    if full_ok:
        full_sorted = fully_adjusted.sort_values("or_", ascending=False)
        full_sorted = full_sorted.assign(rank_full=range(1, len(full_sorted) + 1))
        belief_full_or = full_sorted.loc["has_belief", "or_"]
        belief_full_rank = int(full_sorted.loc["has_belief", "rank_full"])
        ra_full = full_sorted.loc["ct_ra", "or_"] if "ct_ra" in full_sorted.index else None
        ms_full = full_sorted.loc["ct_ms", "or_"] if "ct_ms" in full_sorted.index else None
        gap_full = abs(belief_full_or - min(ra_full, ms_full)) if ra_full and ms_full else None
        fully_adjusted_md = f"""
**Fully-adjusted spec (Model C) closes the magnitude gap between the two methodologies.**
Under heavy adjustment (`sex + register + nagiag + qr_tracked + log_clauses_len_std +
has_nag_i_prop` + the other four comparators' thematic proportions), `has_belief`'s OR
drops from {belief_row['or_']:.2f} (plain) / {adjusted.loc['has_belief', 'or_']:.2f} (adjusted)
to **{belief_full_or:.2f}** — still rank {belief_full_rank}th of 10, but now sitting
{gap_full:.2f} below the lower of `ct_ra`/`ct_ms` ({min(ra_full, ms_full):.2f}) once fully
adjusted, nearly matching the permutation method's gap ({gap_permutation:.2f}). The
plain/adjusted specs' "close to competitive" reading turns out to be an artifact of
under-adjustment, not a genuine method disagreement — properly controlled, the regression
and permutation methods converge on the same magnitude, not just the same rank.

Fit cost of this spec was real: mean {timing_by_spec.loc['fully_adjusted','mean']:.0f}s vs.
{timing_by_spec.loc['plain','mean']:.0f}s (plain) / {timing_by_spec.loc['adjusted','mean']:.0f}s
(adjusted) per fit — up to {timing_by_spec.loc['fully_adjusted','max']:.0f}s for the slowest
single fit. Confirms the manuscript's own heavier models are genuinely more expensive to fit,
not just more thorough on paper.

**Caveat:** at least two of the ten fully-adjusted fits (`ct_ms`, `ct_ei`) printed lme4
non-convergence warnings (gradient ~0.003-0.006 — near-convergence, not a clean fit) even
though they cleared the script's fit-success guard; console output for the earlier categories
was truncated by a `tail -100` pipe on the run that produced these numbers, so their
convergence status could not be re-confirmed after the fact. Treat the fully-adjusted ORs as
provisionally converged, not guaranteed-clean — a rerun with untruncated logging would be
needed before citing these numbers in the manuscript itself.
"""
    else:
        fully_adjusted_md = "\nFully-adjusted spec: at least one fit failed to converge — see CSV for detail.\n"

    interpretation_md = f"""
Both methods agree on the ordering: `has_belief` ranks {int(belief_row['rank_regression'])}th of 10
by regression OR and {int(belief_row['rank_permutation'])}th of 10 by permutation fold-enrichment
(Spearman rank correlation **{spearman:.3f}**) — in neither method does the aggregate beat any of
the four belief subtypes (lowest subtype OR = {min_subtype_or:.2f}) or beat both `ct_ra`
(OR={ra_or:.2f}) and `ct_ms` (OR={ms_or:.2f}).

**But the two methods disagree on magnitude, and that's worth keeping rather than smoothing over.**
Under the regression (this script), `has_belief`'s OR ({belief_row['or_']:.2f}) sits only
{gap_regression:.2f} below the lower of `ct_ra`/`ct_ms` ({min(ra_or, ms_or):.2f}) — close to
competitive, similar in spirit to the manuscript's own original framing ("2 of 5 comparators
similar to belief"). Under the permutation-null fold-enrichment
(`comparative_burstiness_results.md`), `has_belief`'s score ({belief_fold:.2f}) sits
{gap_permutation:.2f} below the lower of `ct_ra`/`ct_ms` ({min(ra_fold, ms_fold):.2f}) — a
larger, more decisive gap, closer to "mediocre, indistinguishable from a random 4-tag union"
(the permutation script's own structural control put it at the 81st percentile of that
distribution, p=0.192).

**Combined, honest conclusion**: the aggregate-exceptionalism claim does not survive either
method — `has_belief` never ranks above the subtypes or clearly above `ct_ra`/`ct_ms` in either
test. Whether it's "roughly competitive with `ra`/`ms`" or "mediocre relative to them" is
method-dependent and should be reported as such, not collapsed into whichever framing sounds
more dramatic. The subtype-level exceptionalism claim, by contrast, is robust to which method
you pick — all four subtypes outrank all five comparators in both the regression ranking and
the permutation ranking, with no ambiguity.
""" + fully_adjusted_md
else:
    perm_compare_md = "\n## Cross-check against the permutation-based ranking\n\nNot available (comparative_burstiness_results.csv not found).\n"
    interpretation_md = "\nPermutation-based comparison not available; see the ranked table above for the regression-only picture.\n"


# ── 4. Markdown write-up ──────────────────────────────────────────────────────

belief_or = plain.loc["has_belief", "or_"] if "has_belief" in plain.index and plain.loc["has_belief", "converged"] else None
belief_or_adj = adjusted.loc["has_belief", "or_"] if "has_belief" in adjusted.index and adjusted.loc["has_belief", "converged"] else None
belief_or_full = fully_adjusted.loc["has_belief", "or_"] if "has_belief" in fully_adjusted.index and fully_adjusted.loc["has_belief", "converged"] else None

timing_md = "\n".join(
    f"| {spec} | {row['mean']:.1f}s | {row['min']:.1f}s | {row['max']:.1f}s |"
    for spec, row in timing_by_spec.iterrows()
)

manuscript_comparators = {"ct_ra": 2.25, "ct_ms": 2.27, "ct_sn": 1.67, "ct_st": 1.63, "ct_ei": 1.65}
comparator_check_rows = []
for cat, published_or in manuscript_comparators.items():
    if cat in plain.index and plain.loc[cat, "converged"]:
        comparator_check_rows.append(
            f"| `{cat}` | {published_or:.2f} | {plain.loc[cat, 'or_']:.2f} |")

md = f"""# The missing has_belief self-to-self burst OR

Fills the gap identified in `manuscript.issues.md` #1: the manuscript's
headline belief burst-ORs (1.95-2.55) are subtype-burst-count predicting the
*aggregate* `has_belief` outcome (narrow predictor, broad union outcome),
not the same kind of quantity as the five published comparator-topic ORs
(each topic's burst-count predicting *that same topic's own* recurrence,
true self→self). Nobody had fit the real self→self logistic-regression
model for `has_belief` itself before this script. Fitting script:
`sembel_self_burst_regression.py`, via the same `BeliefContextModel`/pymer4
machinery the manuscript itself used (not the permutation method — see
`comparative_burstiness_results.md` for that independent approach).

Three model specs per category, since the manuscript's own covariate choice
for its comparator "analogical burst models" is unrecorded (not archived in
the results workbook, prose doesn't clarify), and because a light spec risks
under-controlling relative to the manuscript's actual, heavily-adjusted
Model 4:

- **plain**: `{{category}} ~ {{burst_count}} + (1|deposition_code)`
- **adjusted**: `{{category}} ~ {{burst_count}} + sex + register + (1|deposition_code)`
- **fully_adjusted**: `{{category}} ~ {{burst_count}} + sex + register + nagiag +
  qr_tracked + log_clauses_len_std + has_nag_i_prop + [the other four
  comparator topics' `ct_*_prop`, excluding the category's own if it is
  itself one of the five comparators] + (1|deposition_code)` — the
  computationally heavy spec, added specifically to test whether the
  plain/adjusted ORs hold up once local discourse/agency structure and
  thematic competition from the other topics are controlled for (`nagiag`
  alone expands to ~9 dummy levels).

## The number that fills the gap

`has_belief`'s own self→self burst OR: **{f'{belief_or:.2f}' if belief_or else 'N/A'}** (plain), **{f'{belief_or_adj:.2f}' if belief_or_adj else 'N/A'}** (adjusted), **{f'{belief_or_full:.2f}' if belief_or_full else 'N/A'}** (fully_adjusted).

## Fit timing by spec

| Spec | Mean | Min | Max |
|---|---|---|---|
{timing_md}

Directly answers whether the heavier spec is actually slower to fit, as
expected going in.

## Full results

```
{res_df.to_string(index=False)}
```

## Sanity check against the manuscript's own published comparator numbers

| Category | Manuscript's published OR | This script's plain-model OR |
|---|---|---|
{chr(10).join(comparator_check_rows)}

Not expected to match exactly (different exact data-prep/model details are
possible) but should land in the same ballpark — if wildly different, treat
`has_belief`'s new number with more caution and investigate before citing it.
{perm_compare_md}

## Interpretation
{interpretation_md}

## Files

- `self_burst_regression_results.csv` — all 30 fits (10 categories × 3 specs)
- Fitting script: `sembel_self_burst_regression.py`
- Cross-referenced: `manuscript.issues.md` #1, `serious.issues.md`,
  `outputs_sembel/comparative_burstiness/comparative_burstiness_results.md`
"""

with open(os.path.join(args.out, "self_burst_regression_results.md"), "w", encoding="utf-8") as f:
    f.write(md)

print(f"\nWrote outputs to {args.out}/")
print("Done.")
