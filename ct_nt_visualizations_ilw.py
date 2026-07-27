"""
Six visualizations for CT/NT descriptives — INVERSE-LENGTH WEIGHTED variant.
Each deposition contributes equally regardless of length.
Rate = mean across depositions of (CT_count / deposition_length).
Data source: depositions.csv
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
import seaborn as sns
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

# ── Load and prepare data ─────────────────────────────────────────────────────

dep = pd.read_csv('depositions.csv')

# Register mapping: 0=Toulouse, 1=Bologna, 2=Bologna LS
REG_MAP = {0: 'Toulouse', 1: 'Bologna', 2: 'Bologna LS'}
dep['register_label'] = dep['register'].map(REG_MAP)

# Create group label
dep['group'] = dep['register_label'] + '\n' + dep['sex']
GROUP_ORDER = ['Toulouse\nf', 'Toulouse\nm', 'Bologna\nf', 'Bologna\nm',
               'Bologna LS\nf', 'Bologna LS\nm']
GROUPS_SHORT = ['Toul. f', 'Toul. m', 'Bol. f', 'Bol. m', 'Bol.LS f', 'Bol.LS m']

# CT column mapping: internal name -> display name
CT_MAP = {
    'ct_ra':    'Religious action',
    'ct_rb':    'Belief (talk-about)',
    'ct_rb.sm': 'Belief: socio-moral',
    'ct_rb.st': 'Belief: socio-theol.',
    'ct_rb.th': 'Belief: theological',
    'ct_ho':    'Heresy/orthodoxy',
    'ct_ms':    'Material support',
    'ct_sn':    'Social network',
    'ct_st':    'Spatio-temporal',
    'ct_ei':    'Encounter interaction',
    'ct_ea':    'Emotional/affective',
    'ct_lp':    'Legal procedural',
}
CT_COLS = list(CT_MAP.keys())
CT_NAMES = list(CT_MAP.values())

# Compute per-deposition proportions
for col in CT_COLS:
    dep[f'{col}_prop'] = dep[col] / dep['clauses_len']

# Compute ILW rates (mean of per-deposition proportions) per group
def ilw_rates_by_group():
    """Returns dict: CT_display_name -> np.array of 6 ILW rates (as %)."""
    rates = {}
    for col, name in CT_MAP.items():
        group_means = []
        for grp in GROUP_ORDER:
            mask = dep['group'] == grp
            group_means.append(dep.loc[mask, f'{col}_prop'].mean() * 100)
        rates[name] = np.array(group_means)
    return rates

def ilw_stats_by_group():
    """Returns dict: CT_display_name -> list of 6 tuples (mean, median, std) of per-dep proportions."""
    stats = {}
    for col, name in CT_MAP.items():
        group_stats = []
        for grp in GROUP_ORDER:
            mask = dep['group'] == grp
            vals = dep.loc[mask, f'{col}_prop']
            group_stats.append((vals.mean() * 100, vals.median() * 100, vals.std() * 100))
        stats[name] = group_stats
    return stats

ILW_RATES = ilw_rates_by_group()
ILW_STATS = ilw_stats_by_group()

# Group sizes
N_DEPS = np.array([dep[dep['group'] == g].shape[0] for g in GROUP_ORDER])

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

SUPTITLE_SUFFIX = '\n(inverse-length weighted: each deposition contributes equally)'


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 1: Thematic profile heatmap (row-normalized z-scores)
# ═════════════════════════════════════════════════════════════════════════════

def fig1_heatmap():
    rates_matrix = np.array([ILW_RATES[k] for k in CT_NAMES])  # (n_cts, 6)

    # Row-normalize to z-scores
    row_means = rates_matrix.mean(axis=1, keepdims=True)
    row_stds = rates_matrix.std(axis=1, keepdims=True)
    row_stds[row_stds == 0] = 1
    z_matrix = (rates_matrix - row_means) / row_stds

    n_rows = len(CT_NAMES)
    n_cols = len(GROUPS_SHORT)

    # Cluster rows and columns
    row_link = linkage(pdist(z_matrix, metric='euclidean'), method='ward')
    col_link = linkage(pdist(z_matrix.T, metric='euclidean'), method='ward')

    fig = plt.figure(figsize=(11, 8))
    gs = gridspec.GridSpec(2, 3, width_ratios=[0.15, 1, 0.04], height_ratios=[0.15, 1],
                           wspace=0.03, hspace=0.02)

    # Column dendrogram
    ax_col_dendro = fig.add_subplot(gs[0, 1])
    col_dendro = dendrogram(col_link, ax=ax_col_dendro, no_labels=True,
                            color_threshold=0, above_threshold_color='#333333')
    ax_col_dendro.set_xlim(0, 10 * n_cols)
    ax_col_dendro.set_axis_off()
    col_order = col_dendro['leaves']

    # Row dendrogram
    ax_row_dendro = fig.add_subplot(gs[1, 0])
    row_dendro = dendrogram(row_link, ax=ax_row_dendro, orientation='left',
                            no_labels=True, color_threshold=0,
                            above_threshold_color='#333333')
    ax_row_dendro.set_ylim(10 * n_rows, 0)
    ax_row_dendro.set_axis_off()
    row_order = row_dendro['leaves']

    # Reorder
    z_ordered = z_matrix[row_order][:, col_order]
    ordered_ct_names = [CT_NAMES[i] for i in row_order]
    ordered_group_names = [GROUPS_SHORT[i] for i in col_order]

    # Heatmap
    ax_heat = fig.add_subplot(gs[1, 1])
    vmax = np.max(np.abs(z_ordered)) * 0.95
    im = ax_heat.imshow(z_ordered, cmap='RdBu_r', aspect='auto',
                        vmin=-vmax, vmax=vmax)
    ax_heat.set_xlim(-0.5, n_cols - 0.5)
    ax_heat.set_ylim(n_rows - 0.5, -0.5)

    # Annotate cells
    for i in range(z_ordered.shape[0]):
        for j in range(z_ordered.shape[1]):
            val = z_ordered[i, j]
            color = 'white' if abs(val) > vmax * 0.6 else 'black'
            ax_heat.text(j, i, f'{val:.1f}', ha='center', va='center',
                        fontsize=8, color=color,
                        fontweight='bold' if abs(val) > 1.5 else 'normal')

    ax_heat.set_xticks(range(len(ordered_group_names)))
    ax_heat.set_xticklabels(ordered_group_names, fontsize=9)
    ax_heat.set_yticks(range(len(ordered_ct_names)))
    ax_heat.set_yticklabels(ordered_ct_names, fontsize=9)
    ax_heat.tick_params(axis='x', top=True, bottom=False, labeltop=True, labelbottom=False)

    ax_cbar = fig.add_subplot(gs[1, 2])
    cbar = fig.colorbar(im, cax=ax_cbar)
    cbar.set_label('Z-score (row-normalized ILW rate)', fontsize=9)

    fig.suptitle('Fig 1-ILW. Thematic profile heatmap' + SUPTITLE_SUFFIX,
                 fontsize=12, fontweight='bold', y=1.02)

    fig.savefig('fig1_ilw_thematic_heatmap.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig1_ilw_thematic_heatmap.png")


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 2: Stacked proportional bar chart — "discursive budget"
# ═════════════════════════════════════════════════════════════════════════════

def fig2_stacked_bars():
    # Aggregate ILW rates into domains
    belief_all = (ILW_RATES['Belief (talk-about)'] + ILW_RATES['Belief: socio-moral'] +
                  ILW_RATES['Belief: socio-theol.'] + ILW_RATES['Belief: theological'])
    heresy = ILW_RATES['Heresy/orthodoxy']
    detective = (ILW_RATES['Material support'] + ILW_RATES['Social network'] +
                 ILW_RATES['Spatio-temporal'] + ILW_RATES['Encounter interaction'])
    emotional = ILW_RATES['Emotional/affective']
    legal = ILW_RATES['Legal procedural']
    relig_action = ILW_RATES['Religious action']

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
                if v > 2:
                    ax.text(i, b + v/2, f'{v:.1f}%', ha='center', va='center',
                           fontsize=8, fontweight='bold', color='white')
        bottom += vals

    for i in range(6):
        ax.text(i, bottom[i] + 1, f'{bottom[i]:.0f}%', ha='center', va='bottom',
               fontsize=8, color='#333333')

    ax.set_xticks(x)
    ax.set_xticklabels([g.replace('\n', '\n') for g in GROUP_ORDER], fontsize=9)
    ax.set_ylabel('ILW rate (%): mean of per-deposition proportions', fontsize=9)
    ax.set_ylim(0, max(bottom) + 5)
    ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.set_title('Fig 2-ILW. Discursive budget: how groups allocate clause-space' + SUPTITLE_SUFFIX,
                 fontsize=11, fontweight='bold')

    fig.savefig('fig2_ilw_discursive_budget.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig2_ilw_discursive_budget.png")


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 3: Belief subtype composition — small-multiple donut charts
# ═════════════════════════════════════════════════════════════════════════════

def fig3_belief_composition():
    belief_subtypes = ['Belief (talk-about)', 'Belief: socio-moral',
                       'Belief: socio-theol.', 'Belief: theological']
    colors = [BELIEF_COLORS[k] for k in belief_subtypes]

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes_flat = axes.flatten()

    for idx, ax in enumerate(axes_flat):
        grp = GROUP_ORDER[idx]
        # ILW rates for belief subtypes
        ilw_vals = np.array([ILW_RATES[k][idx] for k in belief_subtypes])
        total_ilw = ilw_vals.sum()
        pcts = ilw_vals / total_ilw * 100 if total_ilw > 0 else np.zeros(4)

        wedges, texts = ax.pie(ilw_vals, colors=colors, startangle=90,
                               wedgeprops=dict(width=0.45, edgecolor='white', linewidth=1.5))

        # Annotate with percentages (only if > 5%)
        angles = [(w.theta1 + w.theta2) / 2 for w in wedges]
        for i, (angle, pct) in enumerate(zip(angles, pcts)):
            if pct > 5:
                x_pos = 0.65 * np.cos(np.radians(angle))
                y_pos = 0.65 * np.sin(np.radians(angle))
                ax.text(x_pos, y_pos, f'{pct:.0f}%', ha='center', va='center',
                       fontsize=9, fontweight='bold', color='white')

        # Center: total ILW belief rate
        ax.text(0, 0.08, f'{total_ilw:.1f}%', ha='center', va='center',
               fontsize=11, fontweight='bold')
        ax.text(0, -0.12, f'n={N_DEPS[idx]} deps', ha='center', va='center',
               fontsize=7, color='#555555')

        ax.set_title(grp.replace('\n', ' '), fontsize=10, fontweight='bold', pad=8)

    legend_patches = [mpatches.Patch(color=colors[i], label=belief_subtypes[i])
                     for i in range(4)]
    fig.legend(handles=legend_patches, loc='lower center', ncol=4, fontsize=9,
              frameon=False, bbox_to_anchor=(0.5, -0.02))

    fig.suptitle('Fig 3-ILW. Belief subtype composition' + SUPTITLE_SUFFIX +
                 '\nCenter: total ILW belief rate',
                 fontsize=11, fontweight='bold')
    fig.tight_layout(rect=[0, 0.04, 1, 0.90])

    fig.savefig('fig3_ilw_belief_composition.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig3_ilw_belief_composition.png")


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 4: Diverging bar chart — belief vs. suppressors
# ═════════════════════════════════════════════════════════════════════════════

def fig4_diverging_bars():
    belief_rb = ILW_RATES['Belief (talk-about)']
    belief_sm = ILW_RATES['Belief: socio-moral']
    belief_st = ILW_RATES['Belief: socio-theol.']
    belief_th = ILW_RATES['Belief: theological']

    material = ILW_RATES['Material support']
    spatial = ILW_RATES['Spatio-temporal']
    encounter = ILW_RATES['Encounter interaction']
    social = ILW_RATES['Social network']

    fig, ax = plt.subplots(figsize=(12, 7))

    y = np.arange(6)
    bar_height = 0.55

    # Suppressor stacking (leftward)
    sup_colors = ['#4292c6', '#6baed6', '#9ecae1', '#c6dbef']
    sup_labels = ['Material support', 'Spatio-temporal', 'Encounter interaction', 'Social network']
    sup_data = [material, spatial, encounter, social]

    left_cumul = np.zeros(6)
    for data, color, label in zip(sup_data, sup_colors, sup_labels):
        ax.barh(y, -data, bar_height, left=-left_cumul,
                color=color, label=label, edgecolor='white', linewidth=0.3)
        left_cumul += data

    # Belief stacking (rightward)
    bel_colors = [BELIEF_COLORS['Belief (talk-about)'], BELIEF_COLORS['Belief: socio-moral'],
                  BELIEF_COLORS['Belief: socio-theol.'], BELIEF_COLORS['Belief: theological']]
    bel_labels = ['Belief (talk-about)', 'Belief: socio-moral',
                  'Belief: socio-theol.', 'Belief: theological']
    bel_data = [belief_rb, belief_sm, belief_st, belief_th]

    right_cumul = np.zeros(6)
    for data, color, label in zip(bel_data, bel_colors, bel_labels):
        ax.barh(y, data, bar_height, left=right_cumul,
                color=color, label=label, edgecolor='white', linewidth=0.3)
        right_cumul += data

    # Annotate totals
    for i in range(6):
        ax.text(-left_cumul[i] - 0.5, i, f'{left_cumul[i]:.1f}%',
               ha='right', va='center', fontsize=8, color='#2166ac', fontweight='bold')
        ax.text(right_cumul[i] + 0.5, i, f'{right_cumul[i]:.1f}%',
               ha='left', va='center', fontsize=8, color='#c51b7d', fontweight='bold')

    ax.axvline(0, color='black', linewidth=0.8, zorder=3)

    ax.set_yticks(y)
    ax.set_yticklabels(GROUP_ORDER, fontsize=9)
    ax.set_xlabel('ILW rate (%)', fontsize=10)
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Split legends
    handles, labels = ax.get_legend_handles_labels()
    n_sup = len(sup_labels)
    leg1 = ax.legend(handles[:n_sup], [f'← {l}' for l in labels[:n_sup]],
                     loc='lower left', fontsize=7, framealpha=0.9, title='Suppressor', title_fontsize=8)
    ax.add_artist(leg1)
    ax.legend(handles[n_sup:], [f'{l} →' for l in labels[n_sup:]],
              loc='lower right', fontsize=7, framealpha=0.9, title='Belief', title_fontsize=8)

    ax.set_title('Fig 4-ILW. Hydraulic competition: belief vs. suppressor topics' + SUPTITLE_SUFFIX,
                 fontsize=11, fontweight='bold', pad=12)

    fig.tight_layout()
    fig.savefig('fig4_ilw_diverging_bars.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig4_ilw_diverging_bars.png")


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 5: Sex-difference slope chart
# ═════════════════════════════════════════════════════════════════════════════

def fig5_slope_chart():
    registers = ['Toulouse', 'Bologna', 'Bologna LS']
    reg_indices = [(0, 1), (2, 3), (4, 5)]  # (f_idx, m_idx)

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
            f_rate = ILW_RATES[ct][f_idx]
            m_rate = ILW_RATES[ct][m_idx]

            if ct.startswith('Belief'):
                color, alpha, lw = '#c51b7d', 0.9, 2.0
            elif ct in ['Material support', 'Encounter interaction']:
                color, alpha, lw = '#2166ac', 0.7, 1.2
            else:
                color, alpha, lw = '#666666', 0.6, 1.0

            ax.plot([0, 1], [f_rate, m_rate], color=color, alpha=alpha, linewidth=lw)
            ax.scatter(0, f_rate, color=color, s=45, zorder=5, alpha=alpha,
                      edgecolor='white', linewidth=0.3)
            ax.scatter(1, m_rate, color=color, s=45, zorder=5, alpha=alpha,
                      edgecolor='white', linewidth=0.3)

            male_vals.append((m_rate, ct, color, alpha))

        # Label on right side with de-overlap
        male_vals.sort(key=lambda x: x[0])
        placed = []
        min_gap = 0.5
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

    axes[0].set_ylabel('ILW rate (%)', fontsize=10)

    legend_elements = [
        plt.Line2D([0], [0], color='#c51b7d', lw=2, label='Belief: rb=talk-about, rb.sm/st/th=subtypes'),
        plt.Line2D([0], [0], color='#2166ac', lw=1.2, label='Suppressor: ms=material, ei=encounter'),
        plt.Line2D([0], [0], color='#666666', lw=1, label='Other: ra=relig.action, ho=heresy, em=emotional'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=1,
              fontsize=8, frameon=True, framealpha=0.9, bbox_to_anchor=(0.5, -0.04))

    fig.suptitle('Fig 5-ILW. Sex differences in content topic rates' + SUPTITLE_SUFFIX,
                 fontsize=11, fontweight='bold')
    fig.tight_layout(rect=[0, 0.06, 1, 0.90])

    fig.savefig('fig5_ilw_sex_slopes.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig5_ilw_sex_slopes.png")


# ═════════════════════════════════════════════════════════════════════════════
# FIGURE 6: Per-deposition distribution of PROPORTIONS (not raw counts)
# ═════════════════════════════════════════════════════════════════════════════

def fig6_distribution_summary():
    selected_cts = ['Belief (talk-about)', 'Belief: socio-moral', 'Belief: socio-theol.',
                    'Belief: theological', 'Religious action', 'Material support',
                    'Heresy/orthodoxy', 'Encounter interaction']

    fig, axes = plt.subplots(2, 4, figsize=(16, 8), sharey=False)
    axes_flat = axes.flatten()

    for ct_idx, (ct, ax) in enumerate(zip(selected_cts, axes_flat)):
        stats = ILW_STATS[ct]  # list of 6 (mean, median, std) in %
        x = np.arange(6)

        means = np.array([s[0] for s in stats])
        medians = np.array([s[1] for s in stats])
        stds = np.array([s[2] for s in stats])

        # Clip lower error bar at 0
        lower_err = np.minimum(stds, means)
        upper_err = stds

        # Error bars
        ax.errorbar(x, means, yerr=[lower_err, upper_err], fmt='none', ecolor='#aaaaaa',
                   elinewidth=1.5, capsize=3, capthick=1, zorder=1)

        # Mean dots
        ax.scatter(x, means, color=GROUP_COLORS, s=80, zorder=3, edgecolor='black',
                  linewidth=0.5)
        # Median diamonds
        ax.scatter(x, medians, color=GROUP_COLORS, s=50, zorder=4, marker='D',
                  edgecolor='black', linewidth=0.5)

        # Highlight mean-median divergence
        for i in range(6):
            if means[i] > 0.1 and medians[i] == 0:
                ax.annotate('', xy=(i, medians[i]), xytext=(i, means[i]),
                          arrowprops=dict(arrowstyle='-', color='red', lw=0.8,
                                        linestyle='--'))

        ax.set_xticks(x)
        ax.set_xticklabels(GROUPS_SHORT, fontsize=7, rotation=30, ha='right')
        ax.set_title(ct, fontsize=9, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.2)

        # Y-axis in % with sensible limits
        y_upper = max(means + upper_err) * 1.1
        ax.set_ylim(-0.2, min(y_upper, max(means) * 4 + 1))
        ax.set_ylabel('% of dep. clauses', fontsize=7)

    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='grey',
                  markersize=8, markeredgecolor='black', label='Mean proportion'),
        plt.Line2D([0], [0], marker='D', color='w', markerfacecolor='grey',
                  markersize=7, markeredgecolor='black', label='Median proportion'),
        plt.Line2D([0], [0], color='#aaaaaa', lw=1.5, label='± 1 SD'),
        plt.Line2D([0], [0], color='red', lw=0.8, linestyle='--',
                  label='Mean–median gap (median = 0)'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=4,
              fontsize=9, frameon=False, bbox_to_anchor=(0.5, -0.02))

    fig.suptitle('Fig 6-ILW. Per-deposition proportion distributions' + SUPTITLE_SUFFIX +
                 '\nValues are CT clauses / deposition length, summarized across depositions',
                 fontsize=11, fontweight='bold')
    fig.tight_layout(rect=[0, 0.04, 1, 0.89])

    fig.savefig('fig6_ilw_distribution_summary.png', bbox_inches='tight')
    plt.close(fig)
    print("  Saved fig6_ilw_distribution_summary.png")


# ═════════════════════════════════════════════════════════════════════════════
# Comparison table: raw vs ILW rates
# ═════════════════════════════════════════════════════════════════════════════

def comparison_table():
    """Print a comparison of raw clause-level rates vs ILW rates."""
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

    print("\n=== Raw vs. ILW rates (%) — largest divergences highlighted ===")
    print(f"{'CT':<25} {'Group':<12} {'Raw':>6} {'ILW':>6} {'Diff':>7}")
    print("-" * 60)
    divergences = []
    for ct in CT_NAMES:
        raw = CT_COUNTS_RAW[ct] / TOTAL_CLAUSES * 100
        ilw = ILW_RATES[ct]
        for g in range(6):
            diff = ilw[g] - raw[g]
            divergences.append((abs(diff), ct, GROUPS_SHORT[g], raw[g], ilw[g], diff))

    divergences.sort(reverse=True)
    for _, ct, grp, raw, ilw, diff in divergences[:20]:
        marker = '***' if abs(diff) > 2 else '**' if abs(diff) > 1 else '*' if abs(diff) > 0.5 else ''
        print(f"{ct:<25} {grp:<12} {raw:>5.1f}% {ilw:>5.1f}% {diff:>+6.1f}% {marker}")


# ═════════════════════════════════════════════════════════════════════════════
# Run all
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("Generating ILW visualizations...")
    fig1_heatmap()
    fig2_stacked_bars()
    fig3_belief_composition()
    fig4_diverging_bars()
    fig5_slope_chart()
    fig6_distribution_summary()
    comparison_table()
    print("\nAll 6 ILW figures saved.")
