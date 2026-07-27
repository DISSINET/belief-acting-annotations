"""
Model 2 ("Thematic Saturation," originally framed as "Thematic
Suppression" -- see POST_SUBMISSION_CORRECTIONS.md #3) GLMM findings,
visualized for a general audience. Replaces the earlier
fig4_diverging_bars.png (a plain clause-% comparison with no regression
behind it) with the manuscript's own actual fitted-model finding.

Data source: all_models_results_20260129_121753.xlsx (this repo's root),
sheet M006_Statistics -- Model 2:
  has_belief ~ sex + register + ct_ra_prop + ct_sn_prop + ct_st_prop +
               ct_ms_prop + ct_ei_prop + (1 | deposition_code)
N = 27,850 clauses / 801 depositions. Coefficients hardcoded here (same
convention as ct_nt_visualizations.py's CT_COUNTS) -- every number below is
copied directly from that sheet, not re-fit.

Usage:
    python fig_model2_saturation_coefs.py
"""
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'figure.dpi': 150,
    'savefig.dpi': 200,
})

# label, log-odds, OR, times-less-likely (=1/OR), color
# Colors match ct_nt_visualizations.py's segment palette for the same 5
# topics, so a reader who's seen the budget/heatmap tabs recognizes them.
SUPPRESSION = [
    ("Material support",      -8.090391, 0.000306, 3263, '#6A51A3'),
    ("Encounter interaction",  -6.128110, 0.002181,  459, '#74A9CF'),
    ("Spatio-temporal",       -3.524262, 0.029474, 33.9, '#1B7A72'),
    ("Social network",        -1.958071, 0.141130, 7.09, '#2166AC'),
    ("Religious action",      -1.615913, 0.198709, 5.03, '#4daf4a'),
]

# Two more significant terms from the SAME model, net of the topic content
# above -- free to show, no new fitting required.
OTHER_EFFECTS = [
    ("Male deponent\n(vs. female)",     0.703103, 1.42, '#999999'),
    ("Bologna LS\n(vs. Toulouse)",      0.555627, 1.80, '#d6604d'),
]

fig = plt.figure(figsize=(11, 7.2))
gs = fig.add_gridspec(1, 2, width_ratios=[2.3, 1], wspace=0.45)

# ---- main panel: suppression ranking ----
ax = fig.add_subplot(gs[0, 0])
labels = [s[0] for s in SUPPRESSION]
times_less = [s[3] for s in SUPPRESSION]
colors = [s[4] for s in SUPPRESSION]
y = np.arange(len(labels))[::-1]  # strongest at top

ax.barh(y, times_less, color=colors, edgecolor='#333333', linewidth=0.6, log=True)
ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=11)
ax.set_xlim(1, 6000)
ax.set_xlabel('Times LESS likely a clause also expresses belief (log scale)', fontsize=9.5)
ax.set_title('Fig 4. What predicts belief NOT appearing?\n'
              'Model 2 (GLMM): topic content, controlling for register, sex, and deposition',
              fontsize=12, fontweight='bold')

for yi, tl in zip(y, times_less):
    txt = f'{tl:,.0f}× less likely' if tl >= 100 else f'{tl:.2f}× less likely'
    ax.text(tl * 1.2, yi, txt, va='center', fontsize=9.5, color='#222222')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# ---- secondary panel: two more significant effects, same model ----
ax2 = fig.add_subplot(gs[0, 1])
labels2 = [o[0] for o in OTHER_EFFECTS]
times2 = [o[2] for o in OTHER_EFFECTS]
colors2 = [o[3] for o in OTHER_EFFECTS]
y2 = np.arange(len(labels2))[::-1]
ax2.barh(y2, times2, color=colors2, edgecolor='#333333', linewidth=0.6)
ax2.set_yticks(y2)
ax2.set_yticklabels(labels2, fontsize=10)
ax2.set_xlabel('Times less likely\n(same model)', fontsize=9)
ax2.set_title('Two more significant effects,\nnet of topic content', fontsize=10.5, fontweight='bold')
for yi, tl in zip(y2, times2):
    ax2.text(tl + 0.05, yi, f'{tl:.2f}×', va='center', fontsize=9.5)
ax2.set_xlim(0, 2.3)
ax2.axvline(1, color='#333333', linewidth=1, linestyle='--')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

fig.text(0.5, 0.01,
         'Source: all_models_results_20260129_121753.xlsx, sheet M006_Statistics -- Model 2, N=27,850 clauses / 801 depositions. '
         'All terms shown are statistically significant (p<.05) after controlling for register, sex, and deposition-level random effects.',
         ha='center', fontsize=7.5, color='#555555')

fig.savefig('fig_model2_saturation_coefs.png', bbox_inches='tight')
plt.close(fig)
print("Saved fig_model2_saturation_coefs.png")
