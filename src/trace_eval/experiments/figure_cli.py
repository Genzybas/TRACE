from __future__ import annotations
import argparse
from trace_eval.experiments.figures import generate_figures
p=argparse.ArgumentParser(); p.add_argument('--study',required=True); p.add_argument('--output',required=True); a=p.parse_args(); generate_figures(a.study,a.output); print(f'Figures written to {a.output}')
