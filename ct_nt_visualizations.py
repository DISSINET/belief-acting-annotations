"""
Six visualizations for CT/NT descriptives across register × sex groups.
Data source: ct_nt_descriptives.xlsx
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.transforms as mtransforms
import numpy as np
import seaborn as sns
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import pdist
from matplotlib.patches import FancyBboxPatch
import matplotlib.patches as mpatches
from datetime import datetime

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

# ── Data ──────────────────────────────────────────────────────────────────────

GROUPS = ['Toulouse\nfemale', 'Toulouse\nmale', 'Bologna\nfemale', 'Bologna\nmale',
          'Bologna LS\nfemale', 'Bologna LS\nmale']
GROUPS_SHORT = ['Toul. f', 'Toul. m', 'Bol. f', 'Bol. m', 'Bol.LS f', 'Bol.LS m']

TOTAL_CLAUSES = np.array([1962, 10164, 1667, 9100, 2399, 2558])
N_DEPOSITIONS = np.array([35, 157, 32, 175, 249, 153])

# Raw counts per CT (order: Toul_f, Toul_m, Bol_f, Bol_m, BolLS_f, BolLS_m)
CT_COUNTS = {
    'Religious action':          np.array([166, 749, 61, 316, 108, 56]),
    'Belief (talk-about)':       np.array([37, 56, 50, 188, 12, 17]),
    'Belief: socio-moral':       np.array([55, 128, 60, 191, 265, 167]),
    'Belief: socio-theol.':      np.array([52, 157, 55, 280, 24, 26]),
    'Belief: theological':       np.array([55, 152, 11, 166, 4, 10]),
    'Heresy/orthodoxy':          np.array([86, 627, 127, 630, 35, 33]),
    'Material support':          np.array([135, 781, 112, 636, 40, 152]),
    'Social network':            np.array([231, 1279, 233, 1336, 147, 301]),
    'Spatio-temporal':           np.array([330, 2120, 268, 1515, 86, 356]),
    'Encounter interaction':     np.array([198, 1526, 160, 744, 34, 109]),
    'Emotional/affective':       np.array([27, 77, 27, 106, 122, 71]),
    'Legal procedural':          np.array([134, 817, 202, 1455, 983, 782]),
}

# Per-deposition stats: (mean, median, std)
PERDEP_STATS = {
    'Belief (talk-about)': [
        (1.06, 0, 2.60), (0.36, 0, 0.92), (1.56, 0, 3.18),
        (1.07, 0, 2.83), (0.05, 0, 0.23), (0.11, 0, 0.76)
    ],
    'Belief: socio-moral': [
        (1.57, 0, 3.23), (0.82, 0, 2.56), (1.88, 0, 3.25),
        (1.09, 0, 2.19), (1.06, 1, 1.11), (1.09, 0, 1.78)
    ],
    'Belief: socio-theol.': [
        (1.49, 0, 3.11), (1.00, 0, 2.68), (1.72, 0, 5.16),
        (1.60, 0, 3.71), (0.10, 0, 0.33), (0.17, 0, 0.89)
    ],
    'Belief: theological': [
        (1.57, 0, 3.15), (0.97, 0, 4.01), (0.34, 0, 0.94),
        (0.95, 0, 3.20), (0.02, 0, 0.13), (0.07, 0, 0.66)
    ],
    'Religious action': [
        (4.74, 4, 5.52), (4.77, 2, 6.62), (1.91, 0, 3.05),
        (1.81, 0, 3.74), (0.43, 0, 0.66), (0.37, 0, 0.66)
    ],
    'Material support': [
        (3.86, 2, 4.56), (4.97, 1, 8.23), (3.50, 2.5, 4.10),
        (3.63, 2, 6.21), (0.16, 0, 0.40), (0.99, 0, 3.28)
    ],
    'Heresy/orthodoxy': [
        (2.46, 1, 2.86), (3.99, 2, 6.81), (3.97, 1.5, 5.81),
        (3.60, 2, 5.24), (0.14, 0, 0.56), (0.22, 0, 0.57)
    ],
    'Encounter interaction': [
        (5.66, 4, 4.90), (9.72, 3, 15.51), (5.00, 3.5, 5.38),
        (4.25, 2, 6.37), (0.14, 0, 0.44), (0.71, 0, 1.77)
    ],
}

# Clause rates
CT_RATES = {k: v / TOTAL_CLAUSES * 100 for k, v in CT_COUNTS.items()}

# ── Color palettes ────────────────────────────────────────────────────────────

# Register colors (consistent across all plots)
REG_COLORS = {
    'Toulouse': '#2166ac',    # blue
    'Bologna': '#4dac26',     # green
    'Bologna LS': '#d6604d',  # red-orange
}
GROUP_COLORS = ['#2166ac', '#6baed6', '#4dac26', '#a1d99b', '#d6604d', '#fcae91']

# Belief subtype colors
BELIEF_COLORS = {
    'Belief (talk-about)': '#7f7f7f',      # grey
    'Belief: socio-moral': '#e7298a',       # magenta
    'Belief: socio-theol.': '#7570b3',      # purple
    'Belief: theological': '#d95f02',       # orange
}

# For stacked bars: domain colors
DOMAIN_COLORS = {
    'Belief (all subtypes)': '#e41a1c',
    'Heresy/orthodoxy': '#984ea3',
    'Detective work': '#377eb8',
    'Emotional/affective': '#ff7f00',
    'Legal procedural': '#a65628',
    'Religious action': '#4daf4a',
    'Other tagged': '#999999',
}


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 1: Thematic profile heatmap (row-normalized z-scores)
# ═════════════════════════════════════════════════════════════════════════════

def fig1_heatmap():
    """Popularization-oriented redraw. Changes from the original clustered
    heatmap:
    1. No row dendrogram/clustering. It added a second, harder-to-read
       ordering logic on top of the (meaningful) column clustering, and its
       lines visually crossed the row label text at this figure size. Rows
       are now ordered by a fixed, legible logic instead: the four belief
       subtypes as one block, then the remaining topics by pooled rate.
       The belief/other-topics band label is placed via an axes-fraction
       text offset (not a second subplot squeezed next to the row labels),
       so it can't overlap the row-label text regardless of how long the
       longest label is.
    2. No column dendrogram either, for the same reason plus a second one:
       a scipy dendrogram plotted in its own Axes does not automatically
       share imshow's column-center coordinates/margins, so the rendered
       tree only ever lines up with the heatmap approximately -- exactly
       the "distorted"/misaligned-with-the-labels failure mode a
       popularizing figure can't afford. Column order still comes from the
       same hierarchical clustering (Bologna LS is genuinely the most
       distinct pair), it's just not drawn as a tree -- a plain vertical
       divider marks the split instead, explained in one caption line.
    3. Column labels drop the "f"/"m" text suffix in favor of a small
       circle/square glyph (female/male) placed under each column header --
       same shape convention used in the deposition-composition treemap, so
       a reader who's seen one figure already knows the code in the other.
    """
    ct_names = list(CT_RATES.keys())
    rates_matrix = np.array([CT_RATES[k] for k in ct_names])  # (n_cts, 6)

    # Row-normalize to z-scores
    row_means = rates_matrix.mean(axis=1, keepdims=True)
    row_stds = rates_matrix.std(axis=1, keepdims=True)
    row_stds[row_stds == 0] = 1  # avoid division by zero
    z_matrix = (rates_matrix - row_means) / row_stds

    # Fixed row order: belief subtypes as one block (theological -> generic,
    # matching the warm-color convention used elsewhere), then remaining
    # topics sorted by pooled mean rate, descending.
    belief_names = ['Belief: theological', 'Belief: socio-theol.', 'Belief: socio-moral', 'Belief (talk-about)']
    other_names = [n for n in ct_names if n not in belief_names]
    other_names.sort(key=lambda n: rates_matrix[ct_names.index(n)].mean(), reverse=True)
    row_order_names = belief_names + other_names
    row_order = [ct_names.index(n) for n in row_order_names]
    n_belief = len(belief_names)
    n_rows = len(ct_names)
    n_cols = len(GROUPS_SHORT)

    # Column order still comes from hierarchical clustering (not drawn as a
    # tree, see docstring) -- Bologna LS's two columns come out most distinct.
    col_dist = pdist(z_matrix.T, metric='euclidean')
    col_link = linkage(col_dist, method='ward')
    col_dendro = dendrogram(col_link, no_plot=True)
    col_order = col_dendro['leaves']

    # Reorder
    z_ordered = z_matrix[row_order][:, col_order]
    ordered_ct_names = row_order_names
    # column labels: register name only, sex carried by the icon row below
    REG_ABBR = {'Toul. f': 'Toulouse', 'Toul. m': 'Toulouse', 'Bol. f': 'Bologna', 'Bol. m': 'Bologna',
                'Bol.LS f': 'Bologna LS', 'Bol.LS m': 'Bologna LS'}
    IS_FEMALE = {'Toul. f': True, 'Toul. m': False, 'Bol. f': True, 'Bol. m': False,
                 'Bol.LS f': True, 'Bol.LS m': False}
    ordered_group_short = [GROUPS_SHORT[i] for i in col_order]
    ordered_reg_names = [REG_ABBR[g] for g in ordered_group_short]
    ordered_is_female = [IS_FEMALE[g] for g in ordered_group_short]

    fig = plt.figure(figsize=(11, 8.2))
    gs = gridspec.GridSpec(2, 1, height_ratios=[0.09, 1], hspace=0.04)

    # Icon strip: one circle (female) or square (male) glyph per column,
    # sharing the heatmap's x-axis positions exactly (same subplot width).
    ax_icons = fig.add_subplot(gs[0, 0])
    ax_icons.set_xlim(-0.5, len(ordered_group_short) - 0.5)
    ax_icons.set_ylim(0, 1)
    ax_icons.axis('off')
    for j, is_f in enumerate(ordered_is_female):
        marker = 'o' if is_f else 's'
        ax_icons.plot(j, 0.5, marker=marker, markersize=13, color='#555555',
                     markeredgecolor='none', linestyle='none')

    # Heatmap
    ax_heat = fig.add_subplot(gs[1, 0])
    vmax = np.max(np.abs(z_ordered)) * 0.95
    im = ax_heat.imshow(z_ordered, cmap='RdBu_r', aspect='auto',
                        vmin=-vmax, vmax=vmax)
    ax_heat.set_xlim(-0.5, n_cols - 0.5)
    ax_heat.set_ylim(n_rows - 0.5, -0.5)

    # Annotate cells with z-scores
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

    # vertical divider marking the cluster split (Bologna LS's 2 columns vs.
    # the rest) -- stands in for the dendrogram without the alignment risk
    split_after = sum(1 for g in ordered_group_short if g.startswith('Bol.LS'))
    if 0 < split_after < len(ordered_group_short):
        ax_heat.axvline(split_after - 0.5, color='#222222', linewidth=1.8)
        ax_icons.axvline(split_after - 0.5, color='#222222', linewidth=1.0)

    # separator line + band label between the belief block and the rest --
    # placed via an axes-fraction x-offset (blended transform), well clear of
    # the row-label text, instead of a second cramped subplot.
    ax_heat.axhline(n_belief - 0.5, color='black', linewidth=1.4)
    band_trans = mtransforms.blended_transform_factory(ax_heat.transAxes, ax_heat.transData)
    ax_heat.text(-0.34, (n_belief - 1) / 2, 'Belief', rotation=90, ha='center', va='center',
                 fontsize=10, fontweight='bold', color='#333333', transform=band_trans, clip_on=False)
    ax_heat.text(-0.34, n_belief + (len(ordered_ct_names) - n_belief - 1) / 2, 'Other\ntopics',
                 rotation=90, ha='center', va='center', fontsize=10, fontweight='bold', color='#333333',
                 transform=band_trans, clip_on=False)

    ax_cbar = fig.add_subplot(gs[1, 2])
    cbar = fig.colorbar(im, cax=ax_cbar)
    cbar.set_label('Z-score (row-normalized clause rate)', fontsize=9)

    # icon legend, once
    fig.text(0.30, 0.975, '●', fontsize=13, color='#555555', ha='center', va='center')
    fig.text(0.335, 0.975, 'female deponents', fontsize=9, ha='left', va='center')
    fig.text(0.48, 0.975, '■', fontsize=11, color='#555555', ha='center', va='center')
    fig.text(0.505, 0.975, 'male deponents', fontsize=9, ha='left', va='center')

    fig.suptitle('Fig 1. Thematic profile heatmap\n'
                 'Row-normalized z-scores of clause rates across register × sex groups. '
                 'Columns ordered by overall similarity — the divider marks Bologna LS as the most distinct pair.',
                 fontsize=12, fontweight='bold', y=1.05)

    fig.savefig('fig1_thematic_heatmap.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig1_thematic_heatmap.png")


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 2: Stacked proportional bar chart — "discursive budget"
# ═════════════════════════════════════════════════════════════════════════════

def fig2_stacked_bars():
    # Aggregate into domains
    belief_all = (CT_COUNTS['Belief (talk-about)'] + CT_COUNTS['Belief: socio-moral'] +
                  CT_COUNTS['Belief: socio-theol.'] + CT_COUNTS['Belief: theological'])
    heresy = CT_COUNTS['Heresy/orthodoxy']
    detective = (CT_COUNTS['Material support'] + CT_COUNTS['Social network'] +
                 CT_COUNTS['Spatio-temporal'] + CT_COUNTS['Encounter interaction'])
    emotional = CT_COUNTS['Emotional/affective']
    legal = CT_COUNTS['Legal procedural']
    relig_action = CT_COUNTS['Religious action']

    tagged_total = belief_all + heresy + detective + emotional + legal + relig_action
    # "Other" = anything not in these domains (communal_meal, belief_spread, biographical_narrative
    # aren't in CT_COUNTS but we know total tagged)
    # We'll normalize to total clauses instead

    domains = {
        'Belief (all subtypes)': belief_all,
        'Heresy/orthodoxy': heresy,
        'Detective work': detective,
        'Religious action': relig_action,
        'Emotional/affective': emotional,
        'Legal procedural': legal,
    }

    # Convert to proportions of total clauses
    domain_pcts = {k: v / TOTAL_CLAUSES * 100 for k, v in domains.items()}

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(GROUPS))
    width = 0.6
    bottom = np.zeros(len(GROUPS))

    domain_order = ['Legal procedural', 'Detective work', 'Heresy/orthodoxy',
                    'Religious action', 'Emotional/affective', 'Belief (all subtypes)']

    for domain in domain_order:
        vals = domain_pcts[domain]
        bars = ax.bar(x, vals, width, bottom=bottom, label=domain,
                      color=DOMAIN_COLORS[domain], edgecolor='white', linewidth=0.5)
        # Label belief specifically
        if domain == 'Belief (all subtypes)':
            for i, (v, b) in enumerate(zip(vals, bottom)):
                if v > 2:
                    ax.text(i, b + v/2, f'{v:.1f}%', ha='center', va='center',
                           fontsize=8, fontweight='bold', color='white')
        bottom += vals

    # Add total tagged % on top
    for i in range(len(GROUPS)):
        ax.text(i, bottom[i] + 1, f'{bottom[i]:.0f}%', ha='center', va='bottom',
               fontsize=8, color='#333333')

    ax.set_xticks(x)
    ax.set_xticklabels(GROUPS, fontsize=9)
    ax.set_ylabel('Percentage of all clauses', fontsize=10)
    ax.set_ylim(0, max(bottom) + 5)
    ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.set_title('Fig 2. Discursive budget: how groups allocate clause-space\n'
                 'Content domain proportions of total clauses per register × sex group',
                 fontsize=12, fontweight='bold')

    fig.savefig('fig2_discursive_budget.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig2_discursive_budget.png")


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 3: Belief subtype composition — small-multiple donut charts
# ═════════════════════════════════════════════════════════════════════════════

def fig3_belief_composition():
    belief_subtypes = ['Belief (talk-about)', 'Belief: socio-moral',
                       'Belief: socio-theol.', 'Belief: theological']
    colors = [BELIEF_COLORS[k] for k in belief_subtypes]

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.flatten()

    for idx, ax in enumerate(axes):
        counts = np.array([CT_COUNTS[k][idx] for k in belief_subtypes])
        total = counts.sum()
        pcts = counts / total * 100 if total > 0 else np.zeros(4)

        wedges, texts = ax.pie(counts, colors=colors, startangle=90,
                               wedgeprops=dict(width=0.45, edgecolor='white', linewidth=1.5))

        # Annotate with percentages (only if > 5%)
        angles = [(w.theta1 + w.theta2) / 2 for w in wedges]
        for i, (angle, pct) in enumerate(zip(angles, pcts)):
            if pct > 5:
                x_pos = 0.65 * np.cos(np.radians(angle))
                y_pos = 0.65 * np.sin(np.radians(angle))
                ax.text(x_pos, y_pos, f'{pct:.0f}%', ha='center', va='center',
                       fontsize=9, fontweight='bold', color='white')

        # Center: total belief count and clause rate
        clause_rate = total / TOTAL_CLAUSES[idx] * 100
        ax.text(0, 0.08, f'n={total}', ha='center', va='center', fontsize=10, fontweight='bold')
        ax.text(0, -0.12, f'({clause_rate:.1f}%)', ha='center', va='center',
               fontsize=8, color='#555555')

        ax.set_title(GROUPS[idx].replace('\n', ' '), fontsize=10, fontweight='bold', pad=8)

    # Shared legend
    legend_patches = [mpatches.Patch(color=colors[i], label=belief_subtypes[i])
                     for i in range(4)]
    fig.legend(handles=legend_patches, loc='lower center', ncol=4, fontsize=9,
              frameon=False, bbox_to_anchor=(0.5, -0.02))

    fig.suptitle('Fig 3. Belief subtype composition within each register × sex group\n'
                 'Center values: total belief clauses (clause rate)',
                 fontsize=12, fontweight='bold')
    fig.tight_layout(rect=[0, 0.04, 1, 0.93])

    fig.savefig('fig3_belief_composition.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig3_belief_composition.png")


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 4: Diverging bar chart — belief vs. suppressors
# ═════════════════════════════════════════════════════════════════════════════

def fig4_diverging_bars():
    # Belief subtypes
    belief_rb = CT_RATES['Belief (talk-about)']
    belief_sm = CT_RATES['Belief: socio-moral']
    belief_st = CT_RATES['Belief: socio-theol.']
    belief_th = CT_RATES['Belief: theological']

    # Suppressors
    material = CT_RATES['Material support']
    spatial = CT_RATES['Spatio-temporal']
    encounter = CT_RATES['Encounter interaction']
    social = CT_RATES['Social network']

    fig, ax = plt.subplots(figsize=(12, 7))

    y = np.arange(len(GROUPS))
    bar_height = 0.55

    # Suppressors (left, negative direction)
    sup_colors = ['#4292c6', '#6baed6', '#9ecae1', '#c6dbef']
    sup_labels = ['Material support', 'Spatio-temporal', 'Encounter interaction', 'Social network']
    sup_data = [material, spatial, encounter, social]

    # Suppressors (stack leftward from 0)
    left_cumul = np.zeros(len(GROUPS))
    for data, color, label in zip(sup_data, sup_colors, sup_labels):
        ax.barh(y, -data, bar_height, left=-left_cumul,
                color=color, label=f'{label}', edgecolor='white', linewidth=0.3)
        left_cumul += data

    # Belief (stack rightward from 0)
    bel_colors = [BELIEF_COLORS['Belief (talk-about)'], BELIEF_COLORS['Belief: socio-moral'],
                  BELIEF_COLORS['Belief: socio-theol.'], BELIEF_COLORS['Belief: theological']]
    bel_labels = ['Belief (talk-about)', 'Belief: socio-moral',
                  'Belief: socio-theol.', 'Belief: theological']
    bel_data = [belief_rb, belief_sm, belief_st, belief_th]

    right_cumul = np.zeros(len(GROUPS))
    for data, color, label in zip(bel_data, bel_colors, bel_labels):
        ax.barh(y, data, bar_height, left=right_cumul,
                color=color, label=f'{label}', edgecolor='white', linewidth=0.3)
        right_cumul += data

    # Annotate totals
    for i in range(len(GROUPS)):
        ax.text(-left_cumul[i] - 0.8, i, f'{left_cumul[i]:.1f}%',
               ha='right', va='center', fontsize=8, color='#2166ac', fontweight='bold')
        ax.text(right_cumul[i] + 0.8, i, f'{right_cumul[i]:.1f}%',
               ha='left', va='center', fontsize=8, color='#c51b7d', fontweight='bold')

    # Center line
    ax.axvline(0, color='black', linewidth=0.8, zorder=3)

    ax.set_yticks(y)
    ax.set_yticklabels(GROUPS, fontsize=9)
    ax.set_xlabel('Clause rate (%)', fontsize=10)
    ax.invert_yaxis()

    # Side labels below the plot via xlabel-style annotation
    xlims = ax.get_xlim()
    ax.annotate('Suppressor topics\n(detective work)',
                xy=(xlims[0] * 0.5, len(GROUPS) - 0.2), fontsize=9, color='#2166ac',
                fontstyle='italic', ha='center', va='top')
    ax.annotate('Belief topics',
                xy=(right_cumul.max() * 0.5, len(GROUPS) - 0.2), fontsize=9, color='#c51b7d',
                fontstyle='italic', ha='center', va='top')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Two-column legend
    handles, labels = ax.get_legend_handles_labels()
    # Split into two groups for legend
    n_sup = len(sup_labels)
    sup_handles, bel_handles = handles[:n_sup], handles[n_sup:]
    sup_labs, bel_labs = labels[:n_sup], labels[n_sup:]
    leg1 = ax.legend(sup_handles, [f'← {l}' for l in sup_labs],
                     loc='lower left', fontsize=7, framealpha=0.9, title='Suppressor', title_fontsize=8)
    ax.add_artist(leg1)
    ax.legend(bel_handles, [f'{l} →' for l in bel_labs],
              loc='lower right', fontsize=7, framealpha=0.9, title='Belief', title_fontsize=8)

    ax.set_title('Fig 4. Hydraulic competition: belief vs. suppressor topics\n'
                 'Clause rates extending from center axis',
                 fontsize=12, fontweight='bold', pad=12)

    fig.tight_layout()
    fig.savefig('fig4_diverging_bars.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig4_diverging_bars.png")


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 5: Sex-difference slope chart (paired dot plot)
# ═════════════════════════════════════════════════════════════════════════════

def fig5_slope_chart():
    registers = ['Toulouse', 'Bologna', 'Bologna LS']
    # Indices: (female_idx, male_idx) for each register
    reg_indices = [(0, 1), (2, 3), (4, 5)]

    # Exclude legal_procedural — it dominates Bologna LS scale and obscures all else
    selected_cts = [
        'Belief: socio-moral', 'Belief: socio-theol.', 'Belief: theological',
        'Belief (talk-about)', 'Religious action', 'Heresy/orthodoxy',
        'Material support', 'Encounter interaction', 'Emotional/affective',
    ]

    # Short labels for right-side annotation
    ct_short = {
        'Belief: socio-moral': 'rb.sm',
        'Belief: socio-theol.': 'rb.st',
        'Belief: theological': 'rb.th',
        'Belief (talk-about)': 'rb',
        'Religious action': 'ra',
        'Heresy/orthodoxy': 'ho',
        'Material support': 'ms',
        'Encounter interaction': 'ei',
        'Emotional/affective': 'em',
    }

    fig, axes = plt.subplots(1, 3, figsize=(14, 7), sharey=False)

    for ax_idx, (ax, reg, (f_idx, m_idx)) in enumerate(zip(axes, registers, reg_indices)):
        # Collect male-side values for label placement
        male_vals = []

        for ct_i, ct in enumerate(selected_cts):
            f_rate = CT_RATES[ct][f_idx]
            m_rate = CT_RATES[ct][m_idx]

            # Color by topic domain
            if ct.startswith('Belief'):
                color = '#c51b7d'
                alpha = 0.9
                lw = 2.0
            elif ct in ['Material support', 'Encounter interaction']:
                color = '#2166ac'
                alpha = 0.7
                lw = 1.2
            else:
                color = '#666666'
                alpha = 0.6
                lw = 1.0

            # Draw slope line
            ax.plot([0, 1], [f_rate, m_rate], color=color, alpha=alpha, linewidth=lw)
            # Dots
            ax.scatter(0, f_rate, color=color, s=45, zorder=5, alpha=alpha, edgecolor='white', linewidth=0.3)
            ax.scatter(1, m_rate, color=color, s=45, zorder=5, alpha=alpha, edgecolor='white', linewidth=0.3)

            male_vals.append((m_rate, ct, color, alpha))

        # Label on the right side of each panel — use short labels with manual jitter
        male_vals.sort(key=lambda x: x[0])
        # Simple greedy de-overlap
        placed = []
        min_gap = 0.6  # minimum vertical gap between labels (% points)
        for m_rate, ct, color, alpha in male_vals:
            y_pos = m_rate
            for py in placed:
                if abs(y_pos - py) < min_gap:
                    y_pos = py + min_gap
            placed.append(y_pos)
            ax.text(1.06, y_pos, ct_short[ct], ha='left', va='center',
                   fontsize=7, color=color, alpha=alpha, fontweight='bold')

        ax.set_xlim(-0.05, 1.25)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['Female', 'Male'], fontsize=10)
        ax.set_title(reg, fontsize=11, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(-0.5, None)

    axes[0].set_ylabel('Clause rate (%)', fontsize=10)

    # Legend with full names mapped to short codes
    legend_elements = [
        plt.Line2D([0], [0], color='#c51b7d', lw=2, label='Belief: rb=talk-about, rb.sm/st/th=subtypes'),
        plt.Line2D([0], [0], color='#2166ac', lw=1.2, label='Suppressor: ms=material, ei=encounter'),
        plt.Line2D([0], [0], color='#666666', lw=1, label='Other: ra=relig.action, ho=heresy, em=emotional'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=1,
              fontsize=8, frameon=True, framealpha=0.9, bbox_to_anchor=(0.5, -0.04))

    fig.suptitle('Fig 5. Sex differences in content topic rates within each register\n'
                 'Slope direction shows female-to-male change (legal procedural excluded)',
                 fontsize=12, fontweight='bold')
    fig.tight_layout(rect=[0, 0.06, 1, 0.92])

    fig.savefig('fig5_sex_slopes.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig5_sex_slopes.png")


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 6: Per-deposition distribution summary — mean ± SD with median
# ═════════════════════════════════════════════════════════════════════════════

def fig6_distribution_summary():
    selected_cts = ['Belief (talk-about)', 'Belief: socio-moral', 'Belief: socio-theol.',
                    'Belief: theological', 'Religious action', 'Material support',
                    'Heresy/orthodoxy', 'Encounter interaction']

    fig, axes = plt.subplots(2, 4, figsize=(16, 8), sharey=False)
    axes = axes.flatten()

    for ct_idx, (ct, ax) in enumerate(zip(selected_cts, axes)):
        stats = PERDEP_STATS[ct]
        x = np.arange(len(GROUPS))

        means = np.array([s[0] for s in stats])
        medians = np.array([s[1] for s in stats])
        stds = np.array([s[2] for s in stats])

        # Clip lower error bar at 0 (count data can't go negative)
        lower_err = np.minimum(stds, means)  # don't extend below 0
        upper_err = stds

        # Mean ± SD error bars (asymmetric, clipped at 0)
        ax.errorbar(x, means, yerr=[lower_err, upper_err], fmt='none', ecolor='#aaaaaa',
                   elinewidth=1.5, capsize=3, capthick=1, zorder=1)

        # Mean dots
        ax.scatter(x, means, color=GROUP_COLORS, s=80, zorder=3, edgecolor='black',
                  linewidth=0.5, label='Mean')

        # Median markers (diamonds)
        ax.scatter(x, medians, color=GROUP_COLORS, s=50, zorder=4, marker='D',
                  edgecolor='black', linewidth=0.5, label='Median')

        # Highlight mean-median divergence
        for i in range(len(GROUPS)):
            if means[i] > 0 and medians[i] == 0:
                ax.annotate('', xy=(i, medians[i]), xytext=(i, means[i]),
                          arrowprops=dict(arrowstyle='-', color='red', lw=0.8,
                                        linestyle='--'))

        ax.set_xticks(x)
        ax.set_xticklabels(GROUPS_SHORT, fontsize=7, rotation=30, ha='right')
        ax.set_title(ct, fontsize=9, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.2)

        # Clip y-axis: floor at 0, ceiling to avoid huge SD ranges
        y_upper = max(means + upper_err) * 1.1
        ax.set_ylim(-0.2, min(y_upper, max(means) * 4 + 1))

    # Shared legend at bottom
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='grey',
                  markersize=8, markeredgecolor='black', label='Mean'),
        plt.Line2D([0], [0], marker='D', color='w', markerfacecolor='grey',
                  markersize=7, markeredgecolor='black', label='Median'),
        plt.Line2D([0], [0], color='#aaaaaa', lw=1.5, label='± 1 SD'),
        plt.Line2D([0], [0], color='red', lw=0.8, linestyle='--',
                  label='Mean–median gap (median = 0)'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=4,
              fontsize=9, frameon=False, bbox_to_anchor=(0.5, -0.02))

    fig.suptitle('Fig 6. Per-deposition distributions: mean, median, and spread\n'
                 'Large mean–median gaps indicate zero-inflated distributions '
                 '(most depositions have 0; a few have many)',
                 fontsize=12, fontweight='bold')
    fig.tight_layout(rect=[0, 0.04, 1, 0.92])

    fig.savefig('fig6_distribution_summary.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig6_distribution_summary.png")


# ═════════════════════════════════════════════════════════════════════════════
# Run all
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("Generating visualizations...")
    fig1_heatmap()
    fig2_stacked_bars()
    fig3_belief_composition()
    fig4_diverging_bars()
    fig5_slope_chart()
    fig6_distribution_summary()
    print("\nAll 6 figures saved.")
