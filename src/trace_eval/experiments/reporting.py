"""Manuscript-ready table exports for real TRACE study results."""

from __future__ import annotations

from statistics import mean, stdev
from typing import List

from trace_eval.experiments.analysis import StudyResult


class StudyLaTeXExporter:
    """Export only values computed from validated execution records."""

    @staticmethod
    def export(study: StudyResult) -> str:
        lines: List[str] = ["% Generated from validated TRACE ExecutionRecord JSONL", "% Do not edit numerical values manually.", ""]
        lines.extend([
            r"\begin{table}[H]", r"\centering",
            r"\caption{Cross-agent behavioural characterization.}",
            r"\label{tab:agent_behavioural_characterization}",
            r"\begin{tabular}{lccccc}", r"\toprule",
            r"Agent & Cognitive & Operational & Reliability & $\kappa$ & TRACE Score \\", r"\midrule",
        ])
        for item in study.agents:
            lines.append(
                f"{item.agent_id} & {item.cognitive_mean:.3f} & {item.operational_mean:.3f} & "
                f"{item.reliability_mean:.3f} & {item.confidence_mean:.3f} & {item.final_score_mean:.3f} \\\\"
            )
        lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}", ""])
        lines.extend([
            r"\begin{table}[H]", r"\centering",
            r"\caption{Behavioural stability across agent--task conditions.}",
            r"\label{tab:stability_summary}",
            r"\begin{tabular}{lcccc}", r"\toprule",
            r"Agent & Mean $\kappa$ & Std. Dev. & Conditions & Runs per Condition \\", r"\midrule",
        ])
        for item in study.agents:
            lines.append(
                f"{item.agent_id} & {item.confidence_mean:.3f} & {item.confidence_std:.3f} & "
                f"{item.condition_count} & {study.conditions[0].run_count} \\\\"
            )
        lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}", ""])
        return "\n".join(lines)
