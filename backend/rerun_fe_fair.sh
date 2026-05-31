#!/bin/zsh
# Full FE-fair re-run cascade after equalizing MOHHO's function-evaluation budget.
cd /Users/haowei/Documents/MIAAD/SMART/Harris2/backend
source .venv/bin/activate
set -e
log() { echo "\n========== $1 ($(date +%H:%M:%S)) =========="; }

log "1/15 rerun_base (30 MOHHO + 30 NSGA)";        python3 rerun_base.py        | tail -8
log "2/15 compare_nsga2 (IGD/spacing/refZ)";       python3 compare_nsga2.py     | tail -4
log "3/15 controls (random/NSGA-arch/refsweep)";   python3 controls.py          | tail -6
log "4/15 taguchi_doe (L9 + confirmation + fig)";  python3 taguchi_doe.py       | tail -6
log "5/15 omnibus_visa_paired (6 methods)";        python3 omnibus_visa_paired.py | tail -10
log "6/15 second_instance (5x perturbed)";         python3 second_instance.py   | tail -4
log "7/15 second_problem (MOMKP, 6 methods)";      python3 second_problem.py    | tail -8
log "8/15 more_structures (TSP + PFSP)";           python3 more_structures.py   | tail -8
log "9/15 omnibus_stats (momkp ranks)";            python3 omnibus_stats.py     | tail -8
log "10/15 headroom_sweep (slow ~19min)";          python3 headroom_sweep.py    | tail -4
log "11/15 fig: paper_figures";                    python3 paper_figures.py     2>/dev/null | tail -2 || echo skip
log "12/15 fig: paper_figures2";                   python3 paper_figures2.py    2>/dev/null | tail -2 || echo skip
log "13/15 fig: ladder";                           python3 ladder_figure.py     2>/dev/null | tail -1 || echo skip
log "14/15 fig: ladder2 + gen";                    python3 ladder2_figure.py    2>/dev/null | tail -1; python3 gen_figure.py 2>/dev/null | tail -1 || echo skip
log "DONE ALL";                                    echo "cascade complete"
