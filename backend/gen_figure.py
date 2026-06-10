"""Generalization figure from second_instance.json + base (stats_test/controls).

Sized for inclusion at 0.74\\textwidth (LNCS textwidth = 347pt); fonts below are
printed sizes. Colors match the unified method palette (MOHHO blue, random
restart grey, NSGA-II orange)."""
import json
import matplotlib; matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype'] = 42
import matplotlib.pyplot as plt
import numpy as np
R = 'app/data/results/'
plt.rcParams.update({'font.family': 'serif', 'font.size': 7.5,
                     'axes.linewidth': 0.6, 'savefig.bbox': 'tight'})
d = json.load(open(R + 'second_instance.json'))['instances']
st = json.load(open(R + 'stats_test.json')); ctl = json.load(open(R + 'controls.json'))
base = {'mohho': float(np.mean(st['mohho_hv'])),
        'random': ctl['random_restart']['stats']['mean'],
        'nsga': float(np.mean(st['nsga2_hv']))}
labels = ['Base'] + [f'P{r["instance"]}' for r in d]
moh = [base['mohho']] + [r['mohho_hv_mean'] for r in d]
rnd = [base['random']] + [r['random_hv_mean'] for r in d]
nsg = [base['nsga']] + [r['nsga2_hv_mean'] for r in d]
relR = [100 * rnd[i] / moh[i] for i in range(len(moh))]
relN = [100 * nsg[i] / moh[i] for i in range(len(moh))]
x = np.arange(len(labels)); w = 0.26
fig, ax = plt.subplots(figsize=(3.62, 2.18))
b1 = ax.bar(x - w, [100] * len(x), w, color='#2E86DE', alpha=0.88, label='MOHHO (= 100)',
            edgecolor='k', linewidth=0.3)
b2 = ax.bar(x, relR, w, color='#9AA3AF', alpha=0.88, label='Random restart',
            edgecolor='k', linewidth=0.3)
b3 = ax.bar(x + w, relN, w, color='#E67E22', alpha=0.88, label='NSGA-II',
            edgecolor='k', linewidth=0.3)
ax.axhline(100, color='#2E86DE', lw=0.7, ls=':')
ymin = min(min(relR), min(relN)) - 2
ax.set_ylim(ymin, 104.9)
for xi, v in zip(x, relR):                       # random restart: above MOHHO
    ax.text(xi, v + 0.25, f'{v:.1f}', ha='center', va='bottom',
            fontsize=5.9, color='#444')
for xi, v in zip(x, relN):                       # NSGA-II: below MOHHO
    ax.text(xi + w, v + 0.25, f'{v:.1f}', ha='center', va='bottom',
            fontsize=5.9, color='#444')
ax.set_ylabel('Hypervolume, % of MOHHO', fontsize=7.3)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7.0)
ax.set_xlabel('Instance (Base + five perturbed-demand instances P1–P5)', fontsize=7.2)
ax.tick_params(length=2, pad=2)
ax.legend(handles=[b1, b2, b3], loc='lower center', bbox_to_anchor=(0.5, 1.01),
          ncol=3, fontsize=6.8, frameon=False, columnspacing=1.6,
          handlelength=1.3, handletextpad=0.5)
ax.grid(axis='y', alpha=0.25, lw=0.4)
ax.spines[['top', 'right']].set_visible(False)
fig.savefig('../MICAI/figures/generalization.pdf')
fig.savefig('../MICAI/figures/generalization.png', dpi=300)
print('generalization fig:', [f'{v:.1f}' for v in relR], 'random%',
      [f'{v:.1f}' for v in relN], 'nsga%')
