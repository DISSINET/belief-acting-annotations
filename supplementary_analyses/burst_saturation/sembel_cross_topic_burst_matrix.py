"""
Full cross-topic local co-occurrence matrix: which content topics tend to
ACCOMPANY belief locally, vs. the deposition-proportion "suppression" framing
tested in sembel_suppression_ranking.tex / the M006 regression.

Motivation (from the suppression-ranking Q&A thread): the "material support
suppresses belief" finding uses DEPOSITION-LEVEL PROPORTIONS (ct_ms_prop
etc.) as predictors -- a different, additive question from "which topics
co-occur with belief in the same local passage." Checked and ruled out two
worries about that finding (multicollinearity inflation, quasi-separation) --
it's real. But it still can't answer a positive-association, LOCAL-window
question: does a nearby religious-action clause make THIS clause more or
less likely to also be belief? Deposition-proportions can't answer that
(they're computed over the whole deposition, not a local window), and raw
burst counts don't have the same closure-adjacent concerns.

Method: for every ordered pair of content topics (A, B), correlate A's
clause-level binary indicator against B's LOCAL BURST COUNT (rolling sum in
a +/-w clause window around the focal clause, excluding the focal clause
itself, computed within each deposition) -- i.e. "does nearby B predict this
clause is A." Point-biserial correlation (binary vs. continuous), no GLMM
fitting -- this needs to scan ~17 topics x 17 topics x 3 window sizes, too
many pairs for per-pair mixed-model fits, so uses the same phi/point-
biserial-coefficient approach as fu_network_analysis.py's co-occurrence
networks elsewhere in this project, applied to LOCAL windows instead of
whole-deposition counts.

Three window radii: 3 (matches the existing burst_* precomputed columns,
internal consistency check against sembel_subtype_cross_burst.py), 5, 7
(wider windows -- does the pattern hold/strengthen/wash out at a larger
local scope).

Usage:
    conda run -n pymer python sembel_cross_topic_burst_matrix.py
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd
import polars as pl

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--pickle", default=os.path.join("outputs_unrest", "anaclauses.pickle"))
parser.add_argument("--out", default=os.path.join("outputs_sembel", "cross_topic_burst"))
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


# ── Topics: the 17-category CT codebook (extraction_prompts/sembel_focused_model_37.txt)
# plus the has_belief aggregate. ct_is/ct_ot are NaN-coded (only rows where present are
# non-null) rather than clean 0/1 -- fillna(0) below fixes that.
TOPICS = {
    "lp": "ct_lp", "rb_sm": "ct_rb_sm", "rb_st": "ct_rb_st", "rb_th": "ct_rb_th",
    "rb": "ct_rb", "sn": "ct_sn", "is": "ct_is", "ea": "ct_ea", "ra": "ct_ra",
    "st": "ct_st", "ei": "ct_ei", "bn": "ct_bn", "ms": "ct_ms", "ho": "ct_ho",
    "bs": "ct_bs", "cm": "ct_cm", "ot": "ct_ot", "has_belief": "has_belief",
}
BELIEF_LABELS = {"rb_sm", "rb_st", "rb_th", "rb", "has_belief"}

# ── Load ─────────────────────────────────────────────────────────────────────
clause_pdf = pd.read_pickle(_resolve(args.pickle))
clause_pdf.columns = [c.replace("-", "_").replace(".", "_") for c in clause_pdf.columns]

missing = [col for col in TOPICS.values() if col not in clause_pdf.columns]
if missing:
    sys.exit(f"Missing expected topic columns: {missing}")

for col in TOPICS.values():
    clause_pdf[col] = clause_pdf[col].fillna(0).astype(int)

n_pos = {label: int(clause_pdf[col].sum()) for label, col in TOPICS.items()}
print("Topic prevalence (clause-level):")
for label, col in TOPICS.items():
    print(f"  {label:12s} ({col:12s}): {n_pos[label]:5d} ({n_pos[label] / len(clause_pdf) * 100:.2f}%)")

if "clause_position" not in clause_pdf.columns:
    clause_pdf = clause_pdf.sort_values(["deposition_code"]).reset_index(drop=True)
    clause_pdf["clause_position"] = clause_pdf.groupby("deposition_code").cumcount()

data = pl.from_pandas(clause_pdf).sort(["deposition_code", "clause_position"])

# ── For each radius, compute burst counts for every topic, then the full
# point-biserial correlation matrix (target's own indicator vs. context
# topic's nearby burst count) ────────────────────────────────────────────────
all_records = []

for radius in RADII:
    print(f"\n{'=' * 80}\nWINDOW RADIUS = {radius}\n{'=' * 80}")
    window = 2 * radius + 1

    burst_exprs = [
        (pl.col(col).rolling_sum(window_size=window, center=True, min_periods=1).over("deposition_code")
         - pl.col(col)).alias(f"burst__{label}")
        for label, col in TOPICS.items()
    ]
    d = data.with_columns(burst_exprs)
    pdf = d.select(list(TOPICS.values()) + [f"burst__{lbl}" for lbl in TOPICS]).to_pandas()

    for target_label, target_col in TOPICS.items():
        y = pdf[target_col].to_numpy(dtype=float)
        for context_label in TOPICS:
            x = pdf[f"burst__{context_label}"].to_numpy(dtype=float)
            if np.std(x) == 0 or np.std(y) == 0:
                r = np.nan
            else:
                r = float(np.corrcoef(x, y)[0, 1])
            all_records.append(dict(
                radius=radius, target=target_label, context=context_label,
                relationship="same_topic" if target_label == context_label else "cross_topic",
                r=r, target_n_positive=n_pos[target_label],
            ))

    # print a compact belief-focused excerpt for this radius
    print(f"\nBelief-row excerpt (radius={radius}), sorted by r descending:")
    sub = pd.DataFrame([rec for rec in all_records if rec["radius"] == radius and rec["target"] == "has_belief"])
    sub = sub.sort_values("r", ascending=False)
    print(sub[["context", "r", "relationship"]].to_string(index=False))

res_df = pd.DataFrame(all_records)
res_df.to_csv(os.path.join(args.out, "cross_topic_burst_matrix.csv"), index=False)

# wide matrices per radius, for convenience
for radius in RADII:
    wide = res_df[res_df["radius"] == radius].pivot(index="target", columns="context", values="r")
    wide.to_csv(os.path.join(args.out, f"cross_topic_burst_matrix_r{radius}.csv"))

# ── Markdown write-up ────────────────────────────────────────────────────────
md_parts = [
"""# Cross-topic local burst co-occurrence matrix

Answers a different question than `sembel_suppression_ranking.tex` (deposition-
proportion suppression strength): which topics tend to **accompany** belief
**locally** (nearby-clause co-occurrence, point-biserial correlation between a
topic's own clause-level indicator and every OTHER topic's local burst count),
at three window radii (+/-3, +/-5, +/-7 clauses, excluding the focal clause).
Full 17-topic-plus-aggregate matrix, not just belief-focused -- 18x18 per
radius.

No compositional/closure concerns here: burst counts are raw local-window
sums, not deposition-wide proportions, so they don't inherit the "fixed
denominator" issue that a proportion-based measure could raise.
"""
]

for radius in RADII:
    sub = res_df[(res_df["radius"] == radius) & (res_df["target"].isin(BELIEF_LABELS))]
    lines = [f"\n## Window radius +/-{radius}\n"]
    for target in ["has_belief", "rb", "rb_sm", "rb_st", "rb_th"]:
        row = sub[sub["target"] == target].sort_values("r", ascending=False)
        row = row[row["context"] != target]  # exclude self here; same-topic already covered elsewhere
        top3 = row.head(3)
        bot3 = row.tail(3)
        lines.append(f"**`{target}`** (n={n_pos[target]}) -- top accompanying topics: " +
                      ", ".join(f"`{r.context}` (r={r.r:.3f})" for r in top3.itertuples()) +
                      "; most avoided: " +
                      ", ".join(f"`{r.context}` (r={r.r:.3f})" for r in bot3.itertuples()))
    md_parts.append("\n".join(lines))

md_parts.append("""
## Files

- `cross_topic_burst_matrix.csv` -- long format, all pairs x all radii
- `cross_topic_burst_matrix_r{3,5,7}.csv` -- wide topic x topic matrices, one per radius
- Fitting script: `sembel_cross_topic_burst_matrix.py`
- Motivating thread: `sembel_suppression_ranking.tex`, `slides.talk.issues.md` #7
""")

with open(os.path.join(args.out, "cross_topic_burst_matrix_results.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md_parts))

print(f"\nWrote outputs to {args.out}/")
print("Done.")
