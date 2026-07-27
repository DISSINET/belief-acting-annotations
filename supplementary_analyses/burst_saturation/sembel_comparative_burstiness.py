"""
Comparative burstiness: does religious belief actually cluster locally more
than other content topics, once two confounds in the manuscript's own
comparison are controlled?

Manuscript (Performance of Religious Belief_manuscript.docx, Model 4) compares
burst-count logistic-regression odds ratios: belief subtypes range 1.95-2.55,
vs. five comparator topics (religious_action OR=2.25, material_support
OR=2.27, social_network OR=1.67, spatial_temporal OR=1.63,
encounter_interaction OR=1.65), concluding belief shows "a distinct,
intensified clustering dynamic." Documented as an overclaim in
leeds2026/serious.issues.md: religious_action and material_support sit
*inside* belief's own OR range (above 3 of 4 subtypes) -- it's "2 of 5
comparators indistinguishable from belief, 3 lower," not "belief vs.
everything else." Two confounds:

  1. Aggregation confound -- has_belief is a union of 4 subtypes; a union-of-4
     mechanically registers more window co-occurrences than a single flat
     comparator, regardless of real clustering-strength differences.
  2. Base-rate confound -- logistic-regression ORs on rare, differently-
     prevalent binary outcomes aren't directly comparable across categories,
     even at identical true clustering strength.

This script replaces the raw-OR comparison with a permutation-null
clustering score computed identically for every category (4 belief
subtypes, the has_belief aggregate, 5 comparators, plus a structural
control), so aggregation and base rate stop distorting the comparison.

Method, per category C, per deposition:
  - Observed statistic: for every C-tagged clause, count other C-tagged
    clauses within a +/-window sliding window (excluding self), summed over
    the deposition -- the same rolling-window co-occurrence count
    belief_context_analysis2.py's create_contextual_features() computes
    (pattern reused inline, NOT imported -- that module pulls in pymer4/rpy2
    at import time for no reason here; this script needs no R).
  - Null: vectorized Monte Carlo permutation, not a closed-form graph
    formula. A closed form (via wedge/disjoint-edge-pair counting) is exact
    and faster, but easy to get subtly wrong (off-by-one in a degree/wedge
    derivation) and much harder to audit by inspection than "shuffled N
    times." Vectorization removes the runtime pressure that would otherwise
    motivate the closed form: per deposition, one random-rank matrix
    (n_permutations x N) is generated ONCE and reused for every category
    tested in that deposition (a category's tagged set under permutation k
    is just "the k positions with the smallest random rank" -- shared across
    categories, since only k differs).
  - Depositions where a category has <2 or >N-2 tagged clauses are excluded
    (no possible co-occurrence -- 0/0, not informative).

Pooling across depositions sums raw quantities (obs, null mean, null
variance) before computing a ratio/z-score, rather than averaging
per-deposition z-scores or fold-ratios -- depositions range 4-385 clauses,
and an unweighted average would let a thin deposition count as much as a
large one. Corpus-level CIs come from a deposition-level bootstrap (resample
depositions with replacement, sum the precomputed per-deposition triples).

Structural control: draw random unions of 4 non-belief tags (from the pool
of 20 non-belief CT columns) and run the identical pipeline. If has_belief's
own clustering score falls inside the distribution these random unions
produce, that's direct evidence its apparent clustering is at least partly
an aggregation artifact, not evidence of belief-specific stickiness.

Usage:
    conda run -n pymer python sembel_comparative_burstiness.py
    (no R/pymer4 actually used -- runs in plain python3 too, if numpy/pandas/
    scipy are available; conda run is just this project's shared-env habit)
"""
import argparse
import itertools
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy import stats as sstats

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--pickle", default=os.path.join("outputs_unrest", "anaclauses.pickle"))
parser.add_argument("--dep-pickle", default=os.path.join("outputs_unrest", "anadepositions_plus.pickle"),
                     help="not used by this test (clause-level only) -- present for CLI convention parity")
parser.add_argument("--out", default=os.path.join("outputs_sembel", "comparative_burstiness"))
parser.add_argument("--window", type=int, default=3)
parser.add_argument("--min-k", type=int, default=2, help="min tagged clauses per deposition-category to include")
parser.add_argument("--n-permutations", type=int, default=5000, help="MC reps for the 9 real categories")
parser.add_argument("--n-permutations-structural", type=int, default=1000,
                     help="MC reps for structural-control draws (subsampled from the same rank matrix; "
                          "lower precision is fine here since 500 draws already give the empirical spread)")
parser.add_argument("--n-bootstrap", type=int, default=2000, help="across-deposition bootstrap reps for corpus CI")
parser.add_argument("--n-structural-draws", type=int, default=500, help="random union-of-4 draws for structural control")
parser.add_argument("--n-validate-deps", type=int, default=20, help="depositions spot-checked in the validation gate")
parser.add_argument("--alpha", type=float, default=0.05)
parser.add_argument("--seed", type=int, default=42)
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


BELIEF_SUBTYPES = {
    "ct_rb_th": "theological",
    "ct_rb_st": "socio_theological",
    "ct_rb_sm": "socio_moral",
    "ct_rb": "generic_belief",
}
BELIEF_AGGREGATE = {"has_belief": "belief_aggregate"}
COMPARATORS = {
    "ct_ra": "religious_action",
    "ct_ms": "material_support",
    "ct_sn": "social_network",
    "ct_st": "spatial_temporal",
    "ct_ei": "encounter_interaction",
}
REAL_CATEGORIES = {**BELIEF_SUBTYPES, **BELIEF_AGGREGATE, **COMPARATORS}
CATEGORY_TYPE = {**{k: "belief_subtype" for k in BELIEF_SUBTYPES},
                 **{k: "belief_aggregate" for k in BELIEF_AGGREGATE},
                 **{k: "comparator" for k in COMPARATORS}}


# ── 1. Load + prep ────────────────────────────────────────────────────────────
clause_path = _resolve(args.pickle)
df = pd.read_pickle(clause_path)
df.columns = [c.replace("-", "_").replace(".", "_") for c in df.columns]

mismatch = int((((df["ct_rb_th"] > 0) | (df["ct_rb_st"] > 0)
                 | (df["ct_rb_sm"] > 0) | (df["ct_rb"] > 0)).astype(int)
                != df["has_belief"]).sum())
print(f"Sanity check: has_belief vs OR-of-4-subtypes mismatch = {mismatch} rows "
      f"({'OK' if mismatch == 0 else 'WARNING'})")

for col in list(REAL_CATEGORIES):
    df[col] = (df[col] > 0).astype(int)

STRUCTURAL_POOL = [c for c in df.columns if c.startswith("ct_")
                   and c not in BELIEF_SUBTYPES and c not in ("ct_expanded", "ct_NA")]
for col in STRUCTURAL_POOL:
    df[col] = (df[col] > 0).astype(int)
print(f"Structural-control pool: {len(STRUCTURAL_POOL)} non-belief tags")
assert len(STRUCTURAL_POOL) == 20, f"expected 20-tag pool, got {len(STRUCTURAL_POOL)} -- check ct_* column set"

df = df.sort_values(["deposition_code", "clause_position", "id"]).reset_index(drop=True)
df["seq_rank"] = df.groupby("deposition_code").cumcount() + 1
print(f"Loaded: {len(df)} clauses, {df['deposition_code'].nunique()} depositions")

master_rng = np.random.default_rng(args.seed)
draw_rng = np.random.default_rng(args.seed + 1)
structural_draws = [tuple(draw_rng.choice(STRUCTURAL_POOL, size=4, replace=False))
                     for _ in range(args.n_structural_draws)]


# ── 2. Core computation ───────────────────────────────────────────────────────
def build_edges(n, window):
    """0-indexed (i,j) pairs, i<j, j-i<=window -- fixed per deposition length."""
    i_idx, j_idx = [], []
    for i in range(n):
        for j in range(i + 1, min(n, i + 1 + window)):
            i_idx.append(i)
            j_idx.append(j)
    return np.array(i_idx, dtype=np.int64), np.array(j_idx, dtype=np.int64)


def observed_stat(tagged_bool, edges_i, edges_j):
    active = tagged_bool[edges_i] & tagged_bool[edges_j]
    return 2 * int(active.sum())


def null_stats_batch(ranks, k, edges_i, edges_j, n_perm=None):
    """ranks: (n_perm_full, N) int array, rank 0..N-1 per row. Returns
    (null_mean, null_var, null_counts) using the first n_perm rows (subsample
    of the same i.i.d. permutation batch -- valid, just fewer draws)."""
    mat = ranks if n_perm is None else ranks[:n_perm]
    tagged_mask = mat < k
    active = tagged_mask[:, edges_i] & tagged_mask[:, edges_j]
    counts = 2.0 * active.sum(axis=1)
    return counts.mean(), counts.var(ddof=1), counts


records = []  # one row per (deposition, real category)
structural_sums = [{"sum_obs": 0.0, "sum_mean": 0.0, "sum_var": 0.0, "n_deps": 0} for _ in structural_draws]

validate_rows = []  # (dep_code, category, mc_mean, mc_var, independent_mean, independent_var, n)

t0 = time.time()
dep_groups = list(df.groupby("deposition_code", sort=False))
validate_dep_idx = set(master_rng.choice(len(dep_groups),
                                          size=min(args.n_validate_deps, len(dep_groups)), replace=False).tolist())

for gi, (dep_code, g) in enumerate(dep_groups):
    g = g.sort_values("seq_rank")
    n = len(g)
    if n < 2:
        continue
    edges_i, edges_j = build_edges(n, args.window)
    if len(edges_i) == 0:
        continue

    dep_rng = np.random.default_rng(args.seed + 1000 + gi)
    rand = dep_rng.random((args.n_permutations, n))
    ranks = rand.argsort(axis=1).argsort(axis=1)

    for col, label in REAL_CATEGORIES.items():
        tagged = g[col].values.astype(bool)
        k = int(tagged.sum())
        if k < args.min_k or k > n - args.min_k:
            continue
        obs = observed_stat(tagged, edges_i, edges_j)
        null_mean, null_var, null_counts = null_stats_batch(ranks, k, edges_i, edges_j)
        records.append(dict(deposition_code=dep_code, category=col, category_label=label,
                             category_type=CATEGORY_TYPE[col], n=n, k=k,
                             observed=obs, null_mean=null_mean, null_var=null_var))

        if gi in validate_dep_idx and col in ("ct_ms", "ct_rb_sm", "has_belief"):
            indep_rng = np.random.default_rng(10_000_000 + args.seed + gi)
            rand2 = indep_rng.random((args.n_permutations, n))
            ranks2 = rand2.argsort(axis=1).argsort(axis=1)
            _, _, null_counts2 = null_stats_batch(ranks2, k, edges_i, edges_j)
            validate_rows.append((dep_code, col, null_mean, null_var,
                                   null_counts2.mean(), null_counts2.var(ddof=1), args.n_permutations))

    for di, tags in enumerate(structural_draws):
        fake = g[list(tags)].any(axis=1).values.astype(bool)
        k = int(fake.sum())
        if k < args.min_k or k > n - args.min_k:
            continue
        obs = observed_stat(fake, edges_i, edges_j)
        null_mean, null_var, _ = null_stats_batch(ranks, k, edges_i, edges_j, n_perm=args.n_permutations_structural)
        structural_sums[di]["sum_obs"] += obs
        structural_sums[di]["sum_mean"] += null_mean
        structural_sums[di]["sum_var"] += null_var
        structural_sums[di]["n_deps"] += 1

    if (gi + 1) % 200 == 0:
        print(f"  ...{gi + 1}/{len(dep_groups)} depositions ({time.time() - t0:.0f}s elapsed)")

print(f"Core computation done in {time.time() - t0:.0f}s")

rec_df = pd.DataFrame.from_records(records)
rec_df.to_csv(os.path.join(args.out, "per_deposition_category_stats.csv"), index=False)


# ── 3. Validation gate ────────────────────────────────────────────────────────
print("\n" + "=" * 80)
print("VALIDATION GATE -- independent recomputation vs. main computation")
print("=" * 80)
val_df = pd.DataFrame(validate_rows, columns=["deposition_code", "category", "mean_a", "var_a", "mean_b", "var_b", "n_perm"])
if len(val_df):
    val_df["mean_diff_se"] = (val_df["mean_a"] - val_df["mean_b"]) / np.sqrt(
        (val_df["var_a"] + val_df["var_b"]) / val_df["n_perm"])
    max_se = val_df["mean_diff_se"].abs().max()
    print(val_df[["deposition_code", "category", "mean_a", "mean_b", "mean_diff_se"]].to_string(index=False))
    print(f"\nMax |mean difference| in independent-recomputation SE units: {max_se:.2f} "
          f"({'OK, within simulation noise' if max_se < 4 else 'WARNING: check the permutation code'})")
    val_df.to_csv(os.path.join(args.out, "validation_gate.csv"), index=False)
else:
    print("No validation rows produced -- check --n-validate-deps / category filters.")


# ── 4. Pool real categories across depositions, bootstrap CI ────────────────
def pool_and_bootstrap(sub_df, n_bootstrap, rng):
    deps = sub_df["deposition_code"].values
    obs = sub_df["observed"].values.astype(float)
    nmean = sub_df["null_mean"].values.astype(float)
    nvar = sub_df["null_var"].values.astype(float)
    n_deps = len(sub_df)

    sum_obs, sum_mean, sum_var = obs.sum(), nmean.sum(), nvar.sum()
    corpus_z = (sum_obs - sum_mean) / np.sqrt(sum_var) if sum_var > 0 else np.nan
    corpus_fold = sum_obs / sum_mean if sum_mean > 0 else np.nan

    boot_z = np.empty(n_bootstrap)
    boot_fold = np.empty(n_bootstrap)
    idx_pool = np.arange(n_deps)
    for b in range(n_bootstrap):
        sel = rng.choice(idx_pool, size=n_deps, replace=True)
        bo, bm, bv = obs[sel].sum(), nmean[sel].sum(), nvar[sel].sum()
        boot_z[b] = (bo - bm) / np.sqrt(bv) if bv > 0 else np.nan
        boot_fold[b] = bo / bm if bm > 0 else np.nan

    return dict(n_deps_included=n_deps, sum_obs=sum_obs, sum_null_mean=sum_mean, sum_null_var=sum_var,
                corpus_z=corpus_z, corpus_z_ci_low=np.nanpercentile(boot_z, 2.5),
                corpus_z_ci_high=np.nanpercentile(boot_z, 97.5),
                corpus_fold=corpus_fold, corpus_fold_ci_low=np.nanpercentile(boot_fold, 2.5),
                corpus_fold_ci_high=np.nanpercentile(boot_fold, 97.5))


boot_rng = np.random.default_rng(args.seed + 99)
results = []
for col, label in REAL_CATEGORIES.items():
    sub = rec_df[rec_df["category"] == col]
    n_total_deps = df.groupby("deposition_code")[col].sum().gt(0).sum()
    n_total_with_col = df["deposition_code"].nunique()
    pooled = pool_and_bootstrap(sub, args.n_bootstrap, boot_rng)
    z_p = 2 * (1 - sstats.norm.cdf(abs(pooled["corpus_z"]))) if np.isfinite(pooled["corpus_z"]) else np.nan
    results.append(dict(category=col, category_label=label, category_type=CATEGORY_TYPE[col],
                         n_clauses_total=int(df[col].sum()),
                         prevalence_pct=round(100 * df[col].mean(), 3),
                         n_depositions_total=n_total_with_col,
                         n_depositions_excluded_sparse=n_total_with_col - pooled["n_deps_included"],
                         **{k: v for k, v in pooled.items() if k != "n_deps_included"},
                         n_depositions_included=pooled["n_deps_included"],
                         p_value=z_p))

res_df = pd.DataFrame(results)
n_tests = len(res_df)
order = np.argsort(res_df["p_value"].fillna(1.0).values)
holm = np.full(n_tests, np.nan)
sorted_p = res_df["p_value"].fillna(1.0).values[order]
running_max = 0.0
for rank, idx in enumerate(order):
    adj = min(1.0, sorted_p[rank] * (n_tests - rank))
    running_max = max(running_max, adj)
    holm[idx] = running_max
res_df["holm_adjusted_p"] = holm
res_df["rank_by_fold"] = res_df["corpus_fold"].rank(ascending=False).astype(int)
res_df["rank_by_z"] = res_df["corpus_z"].rank(ascending=False).astype(int)
res_df = res_df.sort_values("rank_by_fold")


# ── 5. Structural control summary ─────────────────────────────────────────────
struct_fold = np.array([s["sum_obs"] / s["sum_mean"] if s["sum_mean"] > 0 else np.nan for s in structural_sums])
struct_z = np.array([(s["sum_obs"] - s["sum_mean"]) / np.sqrt(s["sum_var"]) if s["sum_var"] > 0 else np.nan
                      for s in structural_sums])
valid_struct = np.isfinite(struct_fold)
struct_fold_v = struct_fold[valid_struct]
struct_z_v = struct_z[valid_struct]

belief_fold = res_df.loc[res_df["category"] == "has_belief", "corpus_fold"].iloc[0]
belief_z = res_df.loc[res_df["category"] == "has_belief", "corpus_z"].iloc[0]
p_aggregation = float((struct_fold_v >= belief_fold).mean()) if len(struct_fold_v) else np.nan
pct_rank = float(sstats.percentileofscore(struct_fold_v, belief_fold)) if len(struct_fold_v) else np.nan


def _ordinal(n):
    n = int(round(n))
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


ordinal_pct_rank = _ordinal(pct_rank) if np.isfinite(pct_rank) else "n/a"

struct_summary = dict(
    category="structural_control_union4", category_label="random union-of-4 non-belief tags",
    category_type="structural_control", n_draws_valid=int(valid_struct.sum()),
    n_draws_total=args.n_structural_draws,
    fold_mean=float(np.nanmean(struct_fold_v)) if len(struct_fold_v) else np.nan,
    fold_sd=float(np.nanstd(struct_fold_v)) if len(struct_fold_v) else np.nan,
    fold_p5=float(np.nanpercentile(struct_fold_v, 5)) if len(struct_fold_v) else np.nan,
    fold_p95=float(np.nanpercentile(struct_fold_v, 95)) if len(struct_fold_v) else np.nan,
    z_mean=float(np.nanmean(struct_z_v)) if len(struct_z_v) else np.nan,
    z_sd=float(np.nanstd(struct_z_v)) if len(struct_z_v) else np.nan,
    has_belief_fold=float(belief_fold), has_belief_z=float(belief_z),
    has_belief_percentile_in_structural_dist=pct_rank,
    p_aggregation=p_aggregation,
)

draws_df = pd.DataFrame([
    dict(draw_id=i, tag1=t[0], tag2=t[1], tag3=t[2], tag4=t[3],
         corpus_fold=struct_fold[i], corpus_z=struct_z[i])
    for i, t in enumerate(structural_draws)
])
draws_df.to_csv(os.path.join(args.out, "comparative_burstiness_structural_draws.csv"), index=False)

res_out = res_df.copy()
res_out.to_csv(os.path.join(args.out, "comparative_burstiness_results.csv"), index=False)
pd.DataFrame([struct_summary]).to_csv(
    os.path.join(args.out, "comparative_burstiness_structural_summary.csv"), index=False)

print("\n" + "=" * 80)
print("RANKED RESULTS (by fold-enrichment)")
print("=" * 80)
print(res_df[["category", "category_label", "category_type", "corpus_fold", "corpus_fold_ci_low",
              "corpus_fold_ci_high", "corpus_z", "holm_adjusted_p", "n_depositions_included",
              "n_depositions_excluded_sparse"]].to_string(index=False))

print("\n" + "=" * 80)
print("STRUCTURAL CONTROL")
print("=" * 80)
for k, v in struct_summary.items():
    print(f"  {k}: {v}")


# ── 6. Markdown write-up ──────────────────────────────────────────────────────
belief_rows = res_df[res_df["category_type"].isin(["belief_subtype", "belief_aggregate"])]
comp_rows = res_df[res_df["category_type"] == "comparator"]
belief_fold_min = belief_rows.loc[belief_rows["category_type"] == "belief_subtype", "corpus_fold"].min()
above_belief_min = comp_rows[comp_rows["corpus_fold"] >= belief_fold_min]

md = f"""# Comparative burstiness — permutation-corrected re-analysis

Tests whether belief clusters (±{args.window}-clause window) more than other
content topics, replacing the manuscript's raw burst-count odds-ratio
comparison (Model 4) with a permutation-null clustering score computed
identically across every category — controlling for two confounds the raw-OR
comparison doesn't handle: (1) `has_belief` aggregates 4 subtypes into a
union, which mechanically inflates apparent co-occurrence vs. a single flat
comparator; (2) categories have very different base rates, which distorts
logistic-regression OR comparisons even at identical true clustering
strength. See `leeds2026/serious.issues.md` #1 for the full background and
the manuscript passage this re-analyzes.

Fitting script: `sembel_comparative_burstiness.py`. Method: vectorized Monte
Carlo permutation (not a closed-form graph formula — simpler to audit, see
script docstring), {args.n_permutations} permutations per (deposition,
category), corpus-level values are **sums of raw per-deposition statistics**
(not averaged per-deposition ratios — depositions range 4–385 clauses, an
unweighted average would let a thin deposition count as much as a large
one), bootstrapped ({args.n_bootstrap} reps, deposition-level resampling) for
the corpus CI.

## Validation gate

{'Independent recomputation (different RNG stream) agreed with the main computation within simulation noise (max ' + f'{max_se:.2f}' + ' SE across ' + str(len(val_df)) + ' spot-checked deposition/category pairs) — see `validation_gate.csv`.' if len(val_df) else 'Validation rows not generated this run.'}

## Ranked results (all 9 real categories)

| Rank | Category | Type | Fold-enrichment [95% CI] | z [95% CI] | Holm p | Depositions (incl./excl. sparse) |
|---|---|---|---|---|---|---|
""" + "\n".join(
        f"| {int(r.rank_by_fold)} | `{r.category}` ({r.category_label}) | {r.category_type} | "
        f"{r.corpus_fold:.2f} [{r.corpus_fold_ci_low:.2f}, {r.corpus_fold_ci_high:.2f}] | "
        f"{r.corpus_z:.1f} [{r.corpus_z_ci_low:.1f}, {r.corpus_z_ci_high:.1f}] | "
        f"{r.holm_adjusted_p:.4f} | {r.n_depositions_included}/{r.n_depositions_excluded_sparse} |"
        for r in res_df.itertuples()
    ) + f"""

## Does the "2 of 5 vs. 3 of 5" pattern survive the correction?

Manuscript's raw-OR comparison: `ct_ra` (OR=2.25) and `ct_ms` (OR=2.27) sat
inside belief's OR range (1.95–2.55); `ct_sn`/`ct_st`/`ct_ei` (OR 1.63–1.67)
sat below it. On this corrected metric: {len(above_belief_min)} of 5
comparators reach or exceed the lowest belief subtype's fold-enrichment
({belief_fold_min:.2f}) — {', '.join(f'`{c}`' for c in above_belief_min['category']) if len(above_belief_min) else 'none do'}.
{'This reproduces the manuscript' + chr(39) + 's qualitative pattern on a confound-corrected metric.' if len(above_belief_min) == 2 else 'This does NOT cleanly reproduce the manuscript' + chr(39) + 's 2-vs-3 split — see the full ranked table above for the actual pattern once base rate and aggregation are controlled.'}

## Is `has_belief`'s clustering an aggregation artifact?

`has_belief` fold-enrichment: **{belief_fold:.2f}**. Structural control
(random unions of 4 non-belief tags, {struct_summary['n_draws_valid']}/{args.n_structural_draws} valid draws):
mean fold **{struct_summary['fold_mean']:.2f}** (SD {struct_summary['fold_sd']:.2f}),
5th–95th percentile band [{struct_summary['fold_p5']:.2f}, {struct_summary['fold_p95']:.2f}].
`has_belief` sits at the **{ordinal_pct_rank} percentile** of the structural
control's distribution; empirical `p_aggregation` (probability a random
union-of-4 non-belief tags clusters at least as strongly as `has_belief`
does) = **{p_aggregation:.3f}**.

{'This is high enough that a substantial part of has_belief' + chr(39) + 's apparent clustering is plausibly explainable by the union-of-4 construction alone, independent of belief content being special.' if p_aggregation > 0.1 else 'This is low enough that has_belief' + chr(39) + 's clustering is not well explained by the union-of-4 construction alone — the aggregate genuinely clusters more than random 4-tag unions typically do.'}

## Sparsity caveat

`ct_rb_th` (theological) and `ct_rb` (generic belief) are included in only
{int(res_df.loc[res_df['category']=='ct_rb_th','n_depositions_included'].iloc[0])} and
{int(res_df.loc[res_df['category']=='ct_rb','n_depositions_included'].iloc[0])} depositions respectively
(out of 801) after the min-k={args.min_k} exclusion — their CIs are visibly
wider than the other categories'. Don't read a narrow-looking point estimate
for these two as more certain than that sample size supports.

## Discourse mode, not topic?

If `ct_ra`/`ct_ms` (elaborated, explanatory content — describing an act, a
transaction) score closer to belief than `ct_sn`/`ct_st`/`ct_ei` (referential,
list-like content — naming a person, a place, a date) on this corrected
metric too, that favors a "clustering tracks discourse mode, not topic
identity" explanation over "belief is uniquely sticky" — see the ranked
table above and `serious.issues.md`'s discussion of this alternative reading.

## Files

- `comparative_burstiness_results.csv` — the ranked table above, full columns
- `comparative_burstiness_structural_draws.csv` — all {args.n_structural_draws} structural draws, individually
- `comparative_burstiness_structural_summary.csv` — the structural-control summary row
- `per_deposition_category_stats.csv` — raw per-(deposition, category) observed/null values, for audit
- `validation_gate.csv` — the independent-recomputation spot-check
"""

with open(os.path.join(args.out, "comparative_burstiness_results.md"), "w", encoding="utf-8") as f:
    f.write(md)

print(f"\nWrote outputs to {args.out}/")
print("Done.")
