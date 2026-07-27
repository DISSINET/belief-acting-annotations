"""
Six visualizations for CT/NT descriptives — GLM EMM-NORMALIZED variant.
Uses Estimated Marginal Means from HC3-robust GLM, standardized to 35 clauses.
Data source: 2panels_glm_analysis_hc3_robust.pdf (Panel 1)
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.transforms as mtransforms
import numpy as np
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import pdist
import matplotlib.patches as mpatches

# ── Global style ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

# ── Data: EMMs from GLM Panel 1 (counts at 35 clauses) ───────────────────────
# Order: 0-f (Toul.f), 0-m (Toul.m), 1-f (Bol.f), 1-m (Bol.m), 2-f (BolLS.f), 2-m (BolLS.m)

GROUPS = ['Toulouse\nfemale', 'Toulouse\nmale', 'Bologna\nfemale', 'Bologna\nmale',
          'Bologna LS\nfemale', 'Bologna LS\nmale']
GROUPS_SHORT = ['Toul. f', 'Toul. m', 'Bol. f', 'Bol. m', 'Bol.LS f', 'Bol.LS m']
STANDARDIZED_LENGTH = 35

# EMM counts (Panel 1) and 95% CIs [lo, hi]
EMM_DATA = {
    'Religious action': {
        'emm': np.array([2.68, 2.16, 1.14, 0.92, 0.59, 0.48]),
        'lo':  np.array([2.0, 1.8, 0.8, 0.7, 0.4, 0.3]),
        'hi':  np.array([3.6, 2.7, 1.6, 1.2, 1.0, 0.8]),
    },
    'Belief (talk-about)': {
        'emm': np.array([0.61, 0.25, 1.27, 0.52, 0.55, 0.23]),
        'lo':  np.array([0.4, 0.2, 0.7, 0.4, 0.3, 0.1]),
        'hi':  np.array([1.1, 0.4, 2.2, 0.7, 1.2, 0.4]),
    },
    'Belief: socio-moral': {
        'emm': np.array([0.80, 0.49, 1.16, 0.70, 3.94, 2.39]),
        'lo':  np.array([0.6, 0.4, 0.8, 0.6, 3.3, 1.9]),
        'hi':  np.array([1.1, 0.6, 1.6, 0.9, 4.7, 3.0]),
    },
    'Belief: socio-theol.': {
        'emm': np.array([0.66, 0.66, 0.99, 1.00, 0.32, 0.33]),
        'lo':  np.array([0.4, 0.5, 0.6, 0.7, 0.2, 0.2]),
        'hi':  np.array([1.1, 0.9, 1.7, 1.4, 0.5, 0.5]),
    },
    'Belief: theological': {
        'emm': np.array([0.49, 0.43, 0.45, 0.38, 0.14, 0.12]),
        'lo':  np.array([0.2, 0.2, 0.2, 0.2, 0.1, 0.1]),
        'hi':  np.array([1.1, 0.8, 1.1, 0.7, 0.4, 0.3]),
    },
    'Heresy/orthodoxy': {
        'emm': np.array([1.93, 1.98, 2.01, 2.06, 0.71, 0.73]),
        'lo':  np.array([1.5, 1.6, 1.5, 1.7, 0.4, 0.5]),
        'hi':  np.array([2.6, 2.4, 2.7, 2.5, 1.2, 1.2]),
    },
    'Material support': {
        'emm': np.array([1.94, 2.01, 2.32, 2.41, 2.97, 3.08]),
        'lo':  np.array([1.4, 1.6, 1.7, 1.9, 1.7, 2.0]),
        'hi':  np.array([2.7, 2.6, 3.2, 3.0, 5.1, 4.7]),
    },
    'Social network': {
        'emm': np.array([4.61, 5.45, 5.02, 5.93, 4.11, 4.85]),
        'lo':  np.array([3.8, 4.8, 4.2, 5.3, 3.1, 3.9]),
        'hi':  np.array([5.5, 6.2, 6.0, 6.6, 5.4, 6.1]),
    },
    'Spatio-temporal': {
        'emm': np.array([5.78, 7.71, 4.79, 6.39, 4.64, 6.17]),
        'lo':  np.array([5.0, 7.0, 4.1, 5.8, 3.7, 5.1]),
        'hi':  np.array([6.7, 8.5, 5.6, 7.0, 5.9, 7.5]),
    },
    'Encounter interaction': {
        'emm': np.array([3.03, 3.58, 2.35, 2.76, 1.49, 1.76]),
        'lo':  np.array([2.3, 3.0, 1.8, 2.3, 1.0, 1.2]),
        'hi':  np.array([3.9, 4.3, 3.0, 3.3, 2.2, 2.5]),
    },
    'Emotional/affective': {
        'emm': np.array([0.44, 0.27, 0.64, 0.40, 1.71, 1.05]),
        'lo':  np.array([0.3, 0.2, 0.5, 0.3, 1.4, 0.8]),
        'hi':  np.array([0.6, 0.4, 0.9, 0.5, 2.1, 1.4]),
    },
    'Legal procedural': {
        'emm': np.array([3.73, 4.35, 5.61, 6.55, 7.91, 9.23]),
        'lo':  np.array([3.2, 3.9, 4.9, 6.0, 6.5, 7.9]),
        'hi':  np.array([4.3, 4.8, 6.5, 7.2, 9.6, 10.8]),
    },
}

# Aggregate belief EMM (from PDF "belief" row)
EMM_BELIEF_AGG = {
    'emm': np.array([2.67, 1.77, 3.94, 2.60, 5.36, 3.54]),
    'lo':  np.array([2.0, 1.4, 3.0, 2.1, 4.1, 2.7]),
    'hi':  np.array([3.5, 2.2, 5.2, 3.2, 7.0, 4.6]),
}

CT_NAMES = list(EMM_DATA.keys())

# Convert EMMs to rates (% of 35 clauses)
EMM_RATES = {k: v['emm'] / STANDARDIZED_LENGTH * 100 for k, v in EMM_DATA.items()}

# ── Color palettes ────────────────────────────────────────────────────────────

GROUP_COLORS = ['#2166ac', '#6baed6', '#4dac26', '#a1d99b', '#d6604d', '#fcae91']

BELIEF_COLORS = {
    'Belief (talk-about)': '#7f7f7f',
    'Belief: socio-moral': '#e7298a',
    'Belief: socio-theol.': '#7570b3',
    'Belief: theological': '#d95f02',
}

DOMAIN_COLORS = {
    'Belief (all subtypes)': '#e41a1c',
    'Heresy/orthodoxy': '#984ea3',
    'Detective work': '#377eb8',
    'Emotional/affective': '#ff7f00',
    'Legal procedural': '#a65628',
    'Religious action': '#4daf4a',
}

SUPTITLE_SUFFIX = '\n(GLM-adjusted EMMs, standardized to 35-clause depositions, HC3 robust)'


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 1: Thematic profile heatmap
# ═════════════════════════════════════════════════════════════════════════════

def fig1_heatmap():
    rates_matrix = np.array([EMM_RATES[k] for k in CT_NAMES])

    # Row-normalize to z-scores
    row_means = rates_matrix.mean(axis=1, keepdims=True)
    row_stds = rates_matrix.std(axis=1, keepdims=True)
    row_stds[row_stds == 0] = 1
    z_matrix = (rates_matrix - row_means) / row_stds

    n_rows = len(CT_NAMES)
    n_cols = len(GROUPS_SHORT)

    # Cluster
    row_link = linkage(pdist(z_matrix, metric='euclidean'), method='ward')
    col_link = linkage(pdist(z_matrix.T, metric='euclidean'), method='ward')

    fig = plt.figure(figsize=(11, 8))
    gs = gridspec.GridSpec(2, 3, width_ratios=[0.15, 1, 0.04], height_ratios=[0.15, 1],
                           wspace=0.03, hspace=0.02)

    ax_col_dendro = fig.add_subplot(gs[0, 1])
    col_dendro = dendrogram(col_link, ax=ax_col_dendro, no_labels=True,
                            color_threshold=0, above_threshold_color='#333333')
    ax_col_dendro.set_xlim(0, 10 * n_cols)
    ax_col_dendro.set_axis_off()
    col_order = col_dendro['leaves']

    ax_row_dendro = fig.add_subplot(gs[1, 0])
    row_dendro = dendrogram(row_link, ax=ax_row_dendro, orientation='left',
                            no_labels=True, color_threshold=0,
                            above_threshold_color='#333333')
    ax_row_dendro.set_ylim(10 * n_rows, 0)
    ax_row_dendro.set_axis_off()
    row_order = row_dendro['leaves']

    z_ordered = z_matrix[row_order][:, col_order]
    ordered_ct_names = [CT_NAMES[i] for i in row_order]
    ordered_group_names = [GROUPS_SHORT[i] for i in col_order]

    # Also get EMM counts for annotation
    emm_matrix = np.array([EMM_DATA[k]['emm'] for k in CT_NAMES])
    emm_ordered = emm_matrix[row_order][:, col_order]

    ax_heat = fig.add_subplot(gs[1, 1])
    vmax = np.max(np.abs(z_ordered)) * 0.95
    im = ax_heat.imshow(z_ordered, cmap='RdBu_r', aspect='auto',
                        vmin=-vmax, vmax=vmax)
    ax_heat.set_xlim(-0.5, n_cols - 0.5)
    ax_heat.set_ylim(n_rows - 0.5, -0.5)

    for i in range(z_ordered.shape[0]):
        for j in range(z_ordered.shape[1]):
            z_val = z_ordered[i, j]
            emm_val = emm_ordered[i, j]
            color = 'white' if abs(z_val) > vmax * 0.6 else 'black'
            # Show z-score with EMM count below
            ax_heat.text(j, i - 0.15, f'{z_val:.1f}', ha='center', va='center',
                        fontsize=8, color=color,
                        fontweight='bold' if abs(z_val) > 1.5 else 'normal')
            ax_heat.text(j, i + 0.2, f'({emm_val:.1f})', ha='center', va='center',
                        fontsize=6, color=color, alpha=0.7)

    ax_heat.set_xticks(range(len(ordered_group_names)))
    ax_heat.set_xticklabels(ordered_group_names, fontsize=9)
    ax_heat.set_yticks(range(len(ordered_ct_names)))
    ax_heat.set_yticklabels(ordered_ct_names, fontsize=9)
    ax_heat.tick_params(axis='x', top=True, bottom=False, labeltop=True, labelbottom=False)

    ax_cbar = fig.add_subplot(gs[1, 2])
    cbar = fig.colorbar(im, cax=ax_cbar)
    cbar.set_label('Z-score (row-normalized EMM rate)', fontsize=9)

    fig.suptitle('Fig 1-EMM. Thematic profile heatmap' + SUPTITLE_SUFFIX,
                 fontsize=11, fontweight='bold', y=1.02)

    fig.savefig('fig1_emm_thematic_heatmap.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig1_emm_thematic_heatmap.png")


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 1-POPULAR: same EMM data, popularized layout ported verbatim from
# ct_nt_visualizations.py::fig1_heatmap (fixed belief/other row block, no
# dendrograms, icon strip for sex) -- the data_snapshot page uses this
# variant, not the dendrogram-heavy fig1_heatmap() above, to keep the
# already-shipped readability work (draft.md §3.5) intact.
# ═════════════════════════════════════════════════════════════════════════════

def fig1_heatmap_popular():
    ct_names = CT_NAMES
    rates_matrix = np.array([EMM_RATES[k] for k in ct_names])

    row_means = rates_matrix.mean(axis=1, keepdims=True)
    row_stds = rates_matrix.std(axis=1, keepdims=True)
    row_stds[row_stds == 0] = 1
    z_matrix = (rates_matrix - row_means) / row_stds

    belief_names = ['Belief: theological', 'Belief: socio-theol.', 'Belief: socio-moral', 'Belief (talk-about)']
    other_names = [n for n in ct_names if n not in belief_names]
    other_names.sort(key=lambda n: rates_matrix[ct_names.index(n)].mean(), reverse=True)
    row_order_names = belief_names + other_names
    row_order = [ct_names.index(n) for n in row_order_names]
    n_belief = len(belief_names)
    n_rows = len(ct_names)
    n_cols = len(GROUPS_SHORT)

    col_dist = pdist(z_matrix.T, metric='euclidean')
    col_link = linkage(col_dist, method='ward')
    col_dendro = dendrogram(col_link, no_plot=True)
    col_order = col_dendro['leaves']

    z_ordered = z_matrix[row_order][:, col_order]
    ordered_ct_names = row_order_names
    REG_ABBR = {'Toul. f': 'Toulouse', 'Toul. m': 'Toulouse', 'Bol. f': 'Bologna', 'Bol. m': 'Bologna',
                'Bol.LS f': 'Bologna LS', 'Bol.LS m': 'Bologna LS'}
    IS_FEMALE = {'Toul. f': True, 'Toul. m': False, 'Bol. f': True, 'Bol. m': False,
                 'Bol.LS f': True, 'Bol.LS m': False}
    ordered_group_short = [GROUPS_SHORT[i] for i in col_order]
    ordered_reg_names = [REG_ABBR[g] for g in ordered_group_short]
    ordered_is_female = [IS_FEMALE[g] for g in ordered_group_short]

    fig = plt.figure(figsize=(11, 8.2))
    gs = gridspec.GridSpec(2, 2, height_ratios=[0.09, 1], width_ratios=[1, 0.04], hspace=0.04, wspace=0.03)

    ax_icons = fig.add_subplot(gs[0, 0])
    ax_icons.set_xlim(-0.5, len(ordered_group_short) - 0.5)
    ax_icons.set_ylim(0, 1)
    ax_icons.axis('off')
    for j, is_f in enumerate(ordered_is_female):
        marker = 'o' if is_f else 's'
        ax_icons.plot(j, 0.5, marker=marker, markersize=13, color='#555555',
                     markeredgecolor='none', linestyle='none')

    ax_heat = fig.add_subplot(gs[1, 0])
    vmax = np.max(np.abs(z_ordered)) * 0.95
    im = ax_heat.imshow(z_ordered, cmap='RdBu_r', aspect='auto',
                        vmin=-vmax, vmax=vmax)
    ax_heat.set_xlim(-0.5, n_cols - 0.5)
    ax_heat.set_ylim(n_rows - 0.5, -0.5)

    for i in range(z_ordered.shape[0]):
        for j in range(z_ordered.shape[1]):
            val = z_ordered[i, j]
            color = 'white' if abs(val) > vmax * 0.6 else 'black'
            ax_heat.text(j, i, f'{val:.1f}', ha='center', va='center',
                        fontsize=8, color=color, fontweight='bold' if abs(val) > 1.5 else 'normal')

    ax_heat.set_xticks(range(len(ordered_reg_names)))
    ax_heat.set_xticklabels(ordered_reg_names, fontsize=9)
    ax_heat.set_yticks(range(len(ordered_ct_names)))
    ax_heat.set_yticklabels(ordered_ct_names, fontsize=9)
    ax_heat.tick_params(axis='x', top=True, bottom=False, labeltop=True, labelbottom=False)

    split_after = sum(1 for g in ordered_group_short if g.startswith('Bol.LS'))
    if 0 < split_after < len(ordered_group_short):
        ax_heat.axvline(split_after - 0.5, color='#222222', linewidth=1.8)
        ax_icons.axvline(split_after - 0.5, color='#222222', linewidth=1.0)

    ax_heat.axhline(n_belief - 0.5, color='black', linewidth=1.4)
    band_trans = mtransforms.blended_transform_factory(ax_heat.transAxes, ax_heat.transData)
    ax_heat.text(-0.34, (n_belief - 1) / 2, 'Belief', rotation=90, ha='center', va='center',
                 fontsize=10, fontweight='bold', color='#333333', transform=band_trans, clip_on=False)
    ax_heat.text(-0.34, n_belief + (len(ordered_ct_names) - n_belief - 1) / 2, 'Other\ntopics',
                 rotation=90, ha='center', va='center', fontsize=10, fontweight='bold', color='#333333',
                 transform=band_trans, clip_on=False)

    ax_cbar = fig.add_subplot(gs[1, 1])
    cbar = fig.colorbar(im, cax=ax_cbar)
    cbar.set_label('Z-score (row-normalized EMM rate)', fontsize=9)

    fig.text(0.30, 0.975, '●', fontsize=13, color='#555555', ha='center', va='center')
    fig.text(0.335, 0.975, 'female deponents', fontsize=9, ha='left', va='center')
    fig.text(0.48, 0.975, '■', fontsize=11, color='#555555', ha='center', va='center')
    fig.text(0.505, 0.975, 'male deponents', fontsize=9, ha='left', va='center')

    fig.suptitle('Fig 1-EMM. Thematic profile heatmap\n'
                 'Row-normalized z-scores of length-adjusted EMM rates (standardized to 35-clause depositions). '
                 'Columns ordered by overall similarity — the divider marks Bologna LS as the most distinct pair.',
                 fontsize=12, fontweight='bold', y=1.05)

    fig.savefig('fig1_emm_popular_thematic_heatmap.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig1_emm_popular_thematic_heatmap.png")
    return row_order_names, ordered_group_short, z_ordered


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 2-POPULAR: same EMM data, popularized layout ported verbatim from
# ct_nt_visualizations.py::fig2_stacked_bars.
# ═════════════════════════════════════════════════════════════════════════════

def fig2_stacked_bars_popular():
    belief_all = EMM_BELIEF_AGG['emm'] / STANDARDIZED_LENGTH * 100
    heresy = EMM_RATES['Heresy/orthodoxy']
    detective = (EMM_RATES['Material support'] + EMM_RATES['Social network'] +
                 EMM_RATES['Spatio-temporal'] + EMM_RATES['Encounter interaction'])
    emotional = EMM_RATES['Emotional/affective']
    legal = EMM_RATES['Legal procedural']
    relig_action = EMM_RATES['Religious action']

    domain_pcts = {
        'Belief (all subtypes)': belief_all,
        'Heresy/orthodoxy': heresy,
        'Detective work': detective,
        'Religious action': relig_action,
        'Emotional/affective': emotional,
        'Legal procedural': legal,
    }

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(6)
    width = 0.6
    bottom = np.zeros(6)

    domain_order = ['Legal procedural', 'Detective work', 'Heresy/orthodoxy',
                    'Religious action', 'Emotional/affective', 'Belief (all subtypes)']

    for domain in domain_order:
        vals = domain_pcts[domain]
        ax.bar(x, vals, width, bottom=bottom, label=domain,
               color=DOMAIN_COLORS[domain], edgecolor='white', linewidth=0.5)
        if domain == 'Belief (all subtypes)':
            for i, (v, b) in enumerate(zip(vals, bottom)):
                if v > 1.5:
                    ax.text(i, b + v/2, f'{v:.1f}%', ha='center', va='center',
                           fontsize=8, fontweight='bold', color='white')
        bottom += vals

    for i in range(6):
        ax.text(i, bottom[i] + 0.5, f'{bottom[i]:.0f}%', ha='center', va='bottom',
               fontsize=8, color='#333333')

    ax.set_xticks(x)
    ax.set_xticklabels(GROUPS, fontsize=9)
    ax.set_ylabel('EMM rate (% of a 35-clause deposition)', fontsize=10)
    ax.set_ylim(0, max(bottom) + 5)
    ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.set_title('Fig 2-EMM. Discursive budget: how groups allocate clause-space\n'
                 'Content domain shares at a common, length-adjusted 35-clause deposition (GLM EMMs)',
                 fontsize=12, fontweight='bold')

    fig.savefig('fig2_emm_popular_discursive_budget.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig2_emm_popular_discursive_budget.png")
    return domain_pcts, bottom


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 2: Stacked proportional bar chart — "discursive budget"
# ═════════════════════════════════════════════════════════════════════════════

def fig2_stacked_bars():
    belief_all = EMM_BELIEF_AGG['emm'] / STANDARDIZED_LENGTH * 100
    heresy = EMM_RATES['Heresy/orthodoxy']
    detective = (EMM_RATES['Material support'] + EMM_RATES['Social network'] +
                 EMM_RATES['Spatio-temporal'] + EMM_RATES['Encounter interaction'])
    emotional = EMM_RATES['Emotional/affective']
    legal = EMM_RATES['Legal procedural']
    relig_action = EMM_RATES['Religious action']

    domain_pcts = {
        'Belief (all subtypes)': belief_all,
        'Heresy/orthodoxy': heresy,
        'Detective work': detective,
        'Religious action': relig_action,
        'Emotional/affective': emotional,
        'Legal procedural': legal,
    }

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(6)
    width = 0.6
    bottom = np.zeros(6)

    domain_order = ['Legal procedural', 'Detective work', 'Heresy/orthodoxy',
                    'Religious action', 'Emotional/affective', 'Belief (all subtypes)']

    for domain in domain_order:
        vals = domain_pcts[domain]
        ax.bar(x, vals, width, bottom=bottom, label=domain,
               color=DOMAIN_COLORS[domain], edgecolor='white', linewidth=0.5)
        if domain == 'Belief (all subtypes)':
            for i, (v, b) in enumerate(zip(vals, bottom)):
                if v > 1.5:
                    ax.text(i, b + v/2, f'{v:.1f}%', ha='center', va='center',
                           fontsize=8, fontweight='bold', color='white')
        bottom += vals

    for i in range(6):
        ax.text(i, bottom[i] + 0.5, f'{bottom[i]:.0f}%', ha='center', va='bottom',
               fontsize=8, color='#333333')

    ax.set_xticks(x)
    ax.set_xticklabels(GROUPS, fontsize=9)
    ax.set_ylabel('EMM rate (% of 35-clause deposition)', fontsize=9)
    ax.set_ylim(0, max(bottom) + 4)
    ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.set_title('Fig 2-EMM. Discursive budget' + SUPTITLE_SUFFIX,
                 fontsize=11, fontweight='bold')

    fig.savefig('fig2_emm_discursive_budget.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig2_emm_discursive_budget.png")


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 3: Belief subtype composition — donut charts with CIs
# ═════════════════════════════════════════════════════════════════════════════

def fig3_belief_composition():
    belief_subtypes = ['Belief (talk-about)', 'Belief: socio-moral',
                       'Belief: socio-theol.', 'Belief: theological']
    colors = [BELIEF_COLORS[k] for k in belief_subtypes]

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes_flat = axes.flatten()

    for idx, ax in enumerate(axes_flat):
        emm_vals = np.array([EMM_DATA[k]['emm'][idx] for k in belief_subtypes])
        total = emm_vals.sum()
        pcts = emm_vals / total * 100 if total > 0 else np.zeros(4)

        wedges, texts = ax.pie(emm_vals, colors=colors, startangle=90,
                               wedgeprops=dict(width=0.45, edgecolor='white', linewidth=1.5))

        angles = [(w.theta1 + w.theta2) / 2 for w in wedges]
        for i, (angle, pct) in enumerate(zip(angles, pcts)):
            if pct > 5:
                x_pos = 0.65 * np.cos(np.radians(angle))
                y_pos = 0.65 * np.sin(np.radians(angle))
                ax.text(x_pos, y_pos, f'{pct:.0f}%', ha='center', va='center',
                       fontsize=9, fontweight='bold', color='white')

        # Center: total EMM belief count and rate
        total_rate = total / STANDARDIZED_LENGTH * 100
        # Also show aggregate belief EMM with CI
        agg = EMM_BELIEF_AGG['emm'][idx]
        agg_lo = EMM_BELIEF_AGG['lo'][idx]
        agg_hi = EMM_BELIEF_AGG['hi'][idx]
        ax.text(0, 0.12, f'{agg:.1f}', ha='center', va='center',
               fontsize=11, fontweight='bold')
        ax.text(0, -0.08, f'[{agg_lo:.1f}, {agg_hi:.1f}]', ha='center', va='center',
               fontsize=7, color='#555555')
        ax.text(0, -0.25, f'({total_rate:.1f}%)', ha='center', va='center',
               fontsize=7, color='#888888')

        ax.set_title(GROUPS[idx].replace('\n', ' '), fontsize=10, fontweight='bold', pad=8)

    legend_patches = [mpatches.Patch(color=colors[i], label=belief_subtypes[i])
                     for i in range(4)]
    fig.legend(handles=legend_patches, loc='lower center', ncol=4, fontsize=9,
              frameon=False, bbox_to_anchor=(0.5, -0.02))

    fig.suptitle('Fig 3-EMM. Belief subtype composition' + SUPTITLE_SUFFIX +
                 '\nCenter: aggregate belief EMM count [95% CI] (rate)',
                 fontsize=10, fontweight='bold')
    fig.tight_layout(rect=[0, 0.04, 1, 0.88])

    fig.savefig('fig3_emm_belief_composition.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig3_emm_belief_composition.png")


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 4: Diverging bar chart with CIs
# ═════════════════════════════════════════════════════════════════════════════

def fig4_diverging_bars():
    sup_keys = ['Material support', 'Spatio-temporal', 'Encounter interaction', 'Social network']
    bel_keys = ['Belief (talk-about)', 'Belief: socio-moral',
                'Belief: socio-theol.', 'Belief: theological']

    sup_colors = ['#4292c6', '#6baed6', '#9ecae1', '#c6dbef']
    bel_colors = [BELIEF_COLORS[k] for k in bel_keys]

    fig, ax = plt.subplots(figsize=(12, 7))

    y = np.arange(6)
    bar_height = 0.55

    # Suppressors (leftward) — use EMM rates
    left_cumul = np.zeros(6)
    for key, color in zip(sup_keys, sup_colors):
        data = EMM_RATES[key]
        ax.barh(y, -data, bar_height, left=-left_cumul,
                color=color, label=key, edgecolor='white', linewidth=0.3)
        left_cumul += data

    # Belief (rightward)
    right_cumul = np.zeros(6)
    for key, color in zip(bel_keys, bel_colors):
        data = EMM_RATES[key]
        ax.barh(y, data, bar_height, left=right_cumul,
                color=color, label=key, edgecolor='white', linewidth=0.3)
        right_cumul += data

    # Annotate totals
    for i in range(6):
        ax.text(-left_cumul[i] - 0.5, i, f'{left_cumul[i]:.1f}%',
               ha='right', va='center', fontsize=8, color='#2166ac', fontweight='bold')
        ax.text(right_cumul[i] + 0.5, i, f'{right_cumul[i]:.1f}%',
               ha='left', va='center', fontsize=8, color='#c51b7d', fontweight='bold')

    ax.axvline(0, color='black', linewidth=0.8, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(GROUPS, fontsize=9)
    ax.set_xlabel('EMM rate (% of 35-clause deposition)', fontsize=10)
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    handles, labels = ax.get_legend_handles_labels()
    n_sup = len(sup_keys)
    leg1 = ax.legend(handles[:n_sup], [f'← {l}' for l in labels[:n_sup]],
                     loc='lower left', fontsize=7, framealpha=0.9, title='Suppressor', title_fontsize=8)
    ax.add_artist(leg1)
    ax.legend(handles[n_sup:], [f'{l} →' for l in labels[n_sup:]],
              loc='lower right', fontsize=7, framealpha=0.9, title='Belief', title_fontsize=8)

    ax.set_title('Fig 4-EMM. Hydraulic competition: belief vs. suppressor topics' + SUPTITLE_SUFFIX,
                 fontsize=10, fontweight='bold', pad=12)

    fig.tight_layout()
    fig.savefig('fig4_emm_diverging_bars.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig4_emm_diverging_bars.png")


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 5: Sex-difference slope chart with CI bands
# ═════════════════════════════════════════════════════════════════════════════

def fig5_slope_chart():
    registers = ['Toulouse', 'Bologna', 'Bologna LS']
    reg_indices = [(0, 1), (2, 3), (4, 5)]

    selected_cts = [
        'Belief: socio-moral', 'Belief: socio-theol.', 'Belief: theological',
        'Belief (talk-about)', 'Religious action', 'Heresy/orthodoxy',
        'Material support', 'Encounter interaction', 'Emotional/affective',
    ]

    ct_short = {
        'Belief: socio-moral': 'rb.sm', 'Belief: socio-theol.': 'rb.st',
        'Belief: theological': 'rb.th', 'Belief (talk-about)': 'rb',
        'Religious action': 'ra', 'Heresy/orthodoxy': 'ho',
        'Material support': 'ms', 'Encounter interaction': 'ei',
        'Emotional/affective': 'em',
    }

    fig, axes = plt.subplots(1, 3, figsize=(14, 7), sharey=False)

    for ax_idx, (ax, reg, (f_idx, m_idx)) in enumerate(zip(axes, registers, reg_indices)):
        male_vals = []

        for ct in selected_cts:
            emm = EMM_DATA[ct]
            f_rate = emm['emm'][f_idx] / STANDARDIZED_LENGTH * 100
            m_rate = emm['emm'][m_idx] / STANDARDIZED_LENGTH * 100

            # CIs as rates
            f_lo = emm['lo'][f_idx] / STANDARDIZED_LENGTH * 100
            f_hi = emm['hi'][f_idx] / STANDARDIZED_LENGTH * 100
            m_lo = emm['lo'][m_idx] / STANDARDIZED_LENGTH * 100
            m_hi = emm['hi'][m_idx] / STANDARDIZED_LENGTH * 100

            if ct.startswith('Belief'):
                color, alpha, lw = '#c51b7d', 0.9, 2.0
            elif ct in ['Material support', 'Encounter interaction']:
                color, alpha, lw = '#2166ac', 0.7, 1.2
            else:
                color, alpha, lw = '#666666', 0.6, 1.0

            # Slope line
            ax.plot([0, 1], [f_rate, m_rate], color=color, alpha=alpha, linewidth=lw)

            # CI error bars at each end
            ax.errorbar(0, f_rate, yerr=[[f_rate - f_lo], [f_hi - f_rate]],
                       fmt='o', color=color, markersize=4, alpha=alpha,
                       ecolor=color, elinewidth=0.8, capsize=2, zorder=5)
            ax.errorbar(1, m_rate, yerr=[[m_rate - m_lo], [m_hi - m_rate]],
                       fmt='o', color=color, markersize=4, alpha=alpha,
                       ecolor=color, elinewidth=0.8, capsize=2, zorder=5)

            male_vals.append((m_rate, ct, color, alpha))

        # Labels with de-overlap
        male_vals.sort(key=lambda x: x[0])
        placed = []
        min_gap = 0.4
        for m_rate, ct, color, alpha in male_vals:
            y_pos = m_rate
            for py in placed:
                if abs(y_pos - py) < min_gap:
                    y_pos = py + min_gap
            placed.append(y_pos)
            ax.text(1.06, y_pos, ct_short[ct], ha='left', va='center',
                   fontsize=7, color=color, alpha=alpha, fontweight='bold')

        ax.set_xlim(-0.1, 1.25)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['Female', 'Male'], fontsize=10)
        ax.set_title(reg, fontsize=11, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(-0.3, None)

    axes[0].set_ylabel('EMM rate (% of 35 clauses)', fontsize=10)

    legend_elements = [
        plt.Line2D([0], [0], color='#c51b7d', lw=2, label='Belief: rb=talk-about, rb.sm/st/th=subtypes'),
        plt.Line2D([0], [0], color='#2166ac', lw=1.2, label='Suppressor: ms=material, ei=encounter'),
        plt.Line2D([0], [0], color='#666666', lw=1, label='Other: ra=relig.action, ho=heresy, em=emotional'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=1,
              fontsize=8, frameon=True, framealpha=0.9, bbox_to_anchor=(0.5, -0.04))

    fig.suptitle('Fig 5-EMM. Sex differences in content topic rates' + SUPTITLE_SUFFIX,
                 fontsize=10, fontweight='bold')
    fig.tight_layout(rect=[0, 0.06, 1, 0.90])

    fig.savefig('fig5_emm_sex_slopes.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig5_emm_sex_slopes.png")


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 6: EMM counts with CIs — forest plot style
# ═════════════════════════════════════════════════════════════════════════════

def fig6_emm_forest():
    """Forest plot of EMM counts with 95% CIs for each CT × group."""
    selected_cts = ['Belief (talk-about)', 'Belief: socio-moral', 'Belief: socio-theol.',
                    'Belief: theological', 'Religious action', 'Material support',
                    'Heresy/orthodoxy', 'Encounter interaction']

    fig, axes = plt.subplots(2, 4, figsize=(16, 8), sharey=False)
    axes_flat = axes.flatten()

    for ct_idx, (ct, ax) in enumerate(zip(selected_cts, axes_flat)):
        emm = EMM_DATA[ct]
        x = np.arange(6)

        means = emm['emm']
        lo = emm['lo']
        hi = emm['hi']

        # CI error bars
        yerr_lo = means - lo
        yerr_hi = hi - means

        for i in range(6):
            ax.errorbar(i, means[i], yerr=[[yerr_lo[i]], [yerr_hi[i]]],
                       fmt='o', color=GROUP_COLORS[i], markersize=7,
                       ecolor=GROUP_COLORS[i], elinewidth=2, capsize=4, capthick=1.5,
                       markeredgecolor='black', markeredgewidth=0.5, zorder=3)

        ax.set_xticks(x)
        ax.set_xticklabels(GROUPS_SHORT, fontsize=7, rotation=30, ha='right')
        ax.set_title(ct, fontsize=9, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.2)
        ax.set_ylabel('EMM count\n(at 35 clauses)', fontsize=7)
        ax.set_ylim(0, None)

    fig.suptitle('Fig 6-EMM. Expected counts with 95% CIs (HC3 robust)' + SUPTITLE_SUFFIX,
                 fontsize=10, fontweight='bold')
    fig.tight_layout(rect=[0, 0.01, 1, 0.90])

    fig.savefig('fig6_emm_forest.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig6_emm_forest.png")


# ═════════════════════════════════════════════════════════════════════════════
# Comparison: raw vs ILW vs EMM
# ═════════════════════════════════════════════════════════════════════════════

def comparison_table():
    TOTAL_CLAUSES = np.array([1962, 10164, 1667, 9100, 2399, 2558])
    CT_COUNTS_RAW = {
        'Religious action':      np.array([166, 749, 61, 316, 108, 56]),
        'Belief (talk-about)':   np.array([37, 56, 50, 188, 12, 17]),
        'Belief: socio-moral':   np.array([55, 128, 60, 191, 265, 167]),
        'Belief: socio-theol.':  np.array([52, 157, 55, 280, 24, 26]),
        'Belief: theological':   np.array([55, 152, 11, 166, 4, 10]),
        'Heresy/orthodoxy':      np.array([86, 627, 127, 630, 35, 33]),
        'Material support':      np.array([135, 781, 112, 636, 40, 152]),
        'Social network':        np.array([231, 1279, 233, 1336, 147, 301]),
        'Spatio-temporal':       np.array([330, 2120, 268, 1515, 86, 356]),
        'Encounter interaction': np.array([198, 1526, 160, 744, 34, 109]),
        'Emotional/affective':   np.array([27, 77, 27, 106, 122, 71]),
        'Legal procedural':      np.array([134, 817, 202, 1455, 983, 782]),
    }

    print("\n=== Three-way comparison: Raw vs EMM rates (% of dep. length) ===")
    print(f"{'CT':<25} {'Group':<12} {'Raw':>6} {'EMM':>6} {'Diff':>7}")
    print("-" * 60)
    for ct in ['Legal procedural', 'Belief: socio-moral', 'Encounter interaction',
               'Material support', 'Religious action']:
        for g in range(6):
            raw = CT_COUNTS_RAW[ct][g] / TOTAL_CLAUSES[g] * 100
            emm = EMM_RATES[ct][g]
            diff = emm - raw
            if abs(diff) > 1:
                print(f"{ct:<25} {GROUPS_SHORT[g]:<12} {raw:>5.1f}% {emm:>5.1f}% {diff:>+6.1f}%")


# ═════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("Generating EMM-normalized visualizations...")
    fig1_heatmap()
    fig2_stacked_bars()
    row_order_names, ordered_group_short, z_ordered = fig1_heatmap_popular()
    domain_pcts, bottom = fig2_stacked_bars_popular()
    print("\n[popular fig1] row order:", row_order_names)
    print("[popular fig1] col order:", ordered_group_short)
    for i, rn in enumerate(row_order_names):
        print(f"  {rn:25s}", [f"{v:.2f}" for v in z_ordered[i]])
    print("\n[popular fig2] domain totals per group:", [f"{b:.1f}" for b in bottom])
    for k, v in domain_pcts.items():
        print(f"  {k:25s}", [f"{x:.1f}" for x in v])
    fig3_belief_composition()
    fig4_diverging_bars()
    fig5_slope_chart()
    fig6_emm_forest()
    comparison_table()
    print("\nAll 6 EMM figures saved.")
