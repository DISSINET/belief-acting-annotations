"""
Asymmetric (before/after) cross-topic local co-occurrence.

Follow-up to sembel_cross_topic_burst_matrix.py, which used a SYMMETRIC
+/-w window and found no topic positively accompanies belief -- stable
across radii 3/5/7, meaning widening the window further would just
converge toward the (already-checked, more negative) deposition-proportion
measure rather than reveal anything new.

A symmetric window can hide a real narrative-SEQUENCE effect: if topic B
characteristically precedes topic A (e.g. "clause identifies who taught the
belief" -> "clause states the belief"), that shows up as a positive
BEFORE-correlation that a symmetric measure could dilute or cancel against
a null/negative AFTER-relationship. This script splits each topic's local
burst count into a BEFORE component (w clauses immediately preceding the
focal clause, not including it) and an AFTER component (w clauses
immediately following), and correlates each separately against every
target topic's clause-level indicator -- same point-biserial approach as
the symmetric script, no GLMM fitting (too many pairs x windows x
before/after splits for per-pair mixed models).

Usage:
    conda run -n pymer python sembel_cross_topic_burst_asymmetric.py
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
import polars as pl

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--pickle", default=os.path.join("outputs_unrest", "anaclauses.pickle"))
parser.add_argument("--out", default=os.path.join("outputs_sembel", "cross_topic_burst_asymmetric"))
parser.add_argument("--radii", default="3,5,7")
args = parser.parse_args()
os.makedirs(args.out, exist_ok=True)
RADII = [int(x) for x in args.radii.split(",")]


def _resolve(path):
    if os.path.isfile(path):
        return path
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(here, path)
    if os.path.isfile(candidate):
        return candidate
    sys.exit(f"File not found. Tried: {path!r} and {candidate!r}")


TOPICS = {
    "lp": "ct_lp", "rb_sm": "ct_rb_sm", "rb_st": "ct_rb_st", "rb_th": "ct_rb_th",
    "rb": "ct_rb", "sn": "ct_sn", "is": "ct_is", "ea": "ct_ea", "ra": "ct_ra",
    "st": "ct_st", "ei": "ct_ei", "bn": "ct_bn", "ms": "ct_ms", "ho": "ct_ho",
    "bs": "ct_bs", "cm": "ct_cm", "ot": "ct_ot", "has_belief": "has_belief",
}
BELIEF_LABELS = {"rb_sm", "rb_st", "rb_th", "rb", "has_belief"}

clause_pdf = pd.read_pickle(_resolve(args.pickle))
clause_pdf.columns = [c.replace("-", "_").replace(".", "_") for c in clause_pdf.columns]

missing = [col for col in TOPICS.values() if col not in clause_pdf.columns]
if missing:
    sys.exit(f"Missing expected topic columns: {missing}")

for col in TOPICS.values():
    clause_pdf[col] = clause_pdf[col].fillna(0).astype(int)

n_pos = {label: int(clause_pdf[col].sum()) for label, col in TOPICS.items()}

if "clause_position" not in clause_pdf.columns:
    clause_pdf = clause_pdf.sort_values(["deposition_code"]).reset_index(drop=True)
    clause_pdf["clause_position"] = clause_pdf.groupby("deposition_code").cumcount()
if "clause_action_id" not in clause_pdf.columns:
    clause_pdf["clause_action_id"] = clause_pdf.index

data = pl.from_pandas(clause_pdf)

all_records = []

for radius in RADII:
    print(f"\n{'=' * 80}\nWINDOW RADIUS = {radius} (asymmetric before/after)\n{'=' * 80}")
    window = radius + 1  # trailing window incl. self; subtract self below

    # BEFORE: ascending order, trailing rolling_sum (current + w previous), minus self
    d_asc = data.sort(["deposition_code", "clause_position"])
    before_exprs = [
        (pl.col(col).rolling_sum(window_size=window, min_samples=1).over("deposition_code")
         - pl.col(col)).alias(f"before__{label}")
        for label, col in TOPICS.items()
    ]
    d_asc = d_asc.with_columns(before_exprs)

    # AFTER: reverse order within each deposition, same trailing trick, then map back
    d_desc = data.sort(["deposition_code", "clause_position"], descending=[False, True])
    after_exprs = [
        (pl.col(col).rolling_sum(window_size=window, min_samples=1).over("deposition_code")
         - pl.col(col)).alias(f"after__{label}")
        for label, col in TOPICS.items()
    ]
    d_desc = d_desc.with_columns(after_exprs)

    merged = d_asc.join(
        d_desc.select(["clause_action_id"] + [f"after__{lbl}" for lbl in TOPICS]),
        on="clause_action_id", how="left",
    )
    pdf = merged.select(
        list(TOPICS.values()) + [f"before__{lbl}" for lbl in TOPICS] + [f"after__{lbl}" for lbl in TOPICS]
    ).to_pandas()

    for target_label, target_col in TOPICS.items():
        y = pdf[target_col].to_numpy(dtype=float)
        for context_label in TOPICS:
            for direction in ("before", "after"):
                x = pdf[f"{direction}__{context_label}"].to_numpy(dtype=float)
                r = np.nan if (np.std(x) == 0 or np.std(y) == 0) else float(np.corrcoef(x, y)[0, 1])
                all_records.append(dict(
                    radius=radius, target=target_label, context=context_label, direction=direction,
                    relationship="same_topic" if target_label == context_label else "cross_topic",
                    r=r, target_n_positive=n_pos[target_label],
                ))

    sub = pd.DataFrame([rec for rec in all_records if rec["radius"] == radius and rec["target"] == "has_belief"
                        and rec["context"] != "has_belief"])
    sub = sub.sort_values("r", ascending=False)
    print(f"\nBelief-row excerpt (radius={radius}), before vs. after, sorted by r descending:")
    print(sub[["context", "direction", "r"]].to_string(index=False))

res_df = pd.DataFrame(all_records)
res_df.to_csv(os.path.join(args.out, "cross_topic_burst_asymmetric.csv"), index=False)

# ── Markdown write-up: for each belief target, show whether before/after
# diverge meaningfully for any context topic (the signal this script exists
# to find) ────────────────────────────────────────────────────────────────
md_parts = ["""# Asymmetric (before/after) cross-topic local co-occurrence

Follow-up to `cross_topic_burst_matrix_results.md` (symmetric +/-w window,
found no topic positively accompanies belief, stable across radii). Splits
each topic's local burst count into BEFORE (w clauses immediately
preceding the focal clause) and AFTER (w clauses immediately following),
to check for a narrative-sequence effect a symmetric window would cancel
out or dilute.
"""]

for radius in RADII:
    lines = [f"\n## Window radius {radius} (before/after, {radius} clauses each direction)\n"]
    for target in ["has_belief", "rb", "rb_sm", "rb_st", "rb_th"]:
        sub = res_df[(res_df["radius"] == radius) & (res_df["target"] == target) & (res_df["context"] != target)]
        piv = sub.pivot(index="context", columns="direction", values="r")
        piv["diff"] = piv["before"] - piv["after"]
        piv = piv.reindex(piv["diff"].abs().sort_values(ascending=False).index)
        top = piv.head(5)
        lines.append(f"**`{target}`** (n={n_pos[target]}) -- top 5 by |before-after| divergence:\n")
        lines.append("| context | before r | after r | before-after |\n|---|---|---|---|")
        for ctx, row in top.iterrows():
            lines.append(f"| `{ctx}` | {row['before']:.3f} | {row['after']:.3f} | {row['diff']:+.3f} |")
        lines.append("")
    md_parts.append("\n".join(lines))

md_parts.append("""
## Interpretation

If no context topic shows a meaningfully large before-after divergence (say
|diff| > 0.05-0.10) for any belief target, that confirms the symmetric
result isn't hiding a directional/sequential effect -- the null (no
thematic companion to belief) is robust to this alternative lens too, not
an artifact of window symmetry.

## Files

- `cross_topic_burst_asymmetric.csv` -- long format, all pairs x radii x direction
- Fitting script: `sembel_cross_topic_burst_asymmetric.py`
- Motivating result: `outputs_sembel/cross_topic_burst/cross_topic_burst_matrix_results.md`
""")

with open(os.path.join(args.out, "cross_topic_burst_asymmetric_results.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_parts))

print(f"\nWrote outputs to {args.out}/")
print("Done.")
