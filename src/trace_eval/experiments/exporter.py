"""
TRACE LaTeX Results Exporter.

Converts ExperimentResult outputs into ready-to-paste LaTeX tables matching
the placeholder tables in Section 5 of the manuscript.
"""

from typing import List
import numpy as np

from trace_eval.experiments.runner import ExperimentResult


class LaTeXExporter:
    """Exports structured LaTeX source code for manuscript tables."""

    @staticmethod
    def export_table_3_characterization(results: List[ExperimentResult]) -> str:
        """Populates Table 3: Behavioural Characterization of Evaluated Agents."""
        lines = [
            r"\begin{table}[H]",
            r"\centering",
            r"\caption{Behavioural Characterization of Evaluated Autonomous LLM Agents}",
            r"\label{tab:agent_behavioural_characterization}",
            r"\begin{tabular}{lccccc}",
            r"\toprule",
            r"\textbf{Agent} & \textbf{Cognitive} & \textbf{Operational} & \textbf{Reliability} & \textbf{Behavioural Confidence} & \textbf{TRACE Score} \\",
            r"\midrule",
        ]
        for res in results:
            sig = res.signature
            trace_score = sig.compute_final_score()
            lines.append(
                f"{res.agent_id} & {sig.cognitive:.3f} & {sig.operational:.3f} & "
                f"{sig.reliability:.3f} & {sig.confidence:.3f} & {trace_score:.3f} \\\\"
            )
        lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
        return "\n".join(lines)

    @staticmethod
    def export_table_5_metrics_vs_trace(results: List[ExperimentResult]) -> str:
        """Populates Table 5: Comparison Between Performance Metrics and TRACE Characterization."""
        lines = [
            r"\begin{table}[H]",
            r"\centering",
            r"\caption{Comparison Between Conventional Performance Metrics and TRACE Characterization}",
            r"\label{tab:metrics_vs_trace}",
            r"\begin{tabular}{lccccc}",
            r"\toprule",
            r"\textbf{Agent} & \textbf{Task Success (\%)} & \textbf{Avg. Latency (s)} & \textbf{Behavioural Confidence ($\kappa$)} & \textbf{TRACE Score} & \textbf{Behavioural Interpretation} \\",
            r"\midrule",
        ]
        for res in results:
            sig = res.signature
            final_score = sig.compute_final_score()
            interp = "Balanced" if final_score > 0.7 else "Variable"
            lines.append(
                f"{res.agent_id} & {res.task_success_rate:.1f} & {res.avg_latency_sec:.2f} & "
                f"{sig.confidence:.3f} & {final_score:.3f} & {interp} \\\\"
            )
        lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
        return "\n".join(lines)

    @staticmethod
    def export_table_7_computational(results: List[ExperimentResult]) -> str:
        """Populates Table 7: Computational Characteristics of TRACE."""
        avg_proc_time = float(np.mean([r.processing_time_ms for r in results]))
        avg_mem = float(np.mean([r.memory_peak_kb for r in results]))
        avg_overhead = float(np.mean([r.protocol_overhead_pct for r in results]))
        total_tasks = sum(r.num_runs for r in results)

        lines = [
            r"\begin{table}[H]",
            r"\centering",
            r"\caption{Computational Characteristics of TRACE}",
            r"\label{tab:trace_computational_characteristics}",
            r"\begin{tabular}{lc}",
            r"\toprule",
            r"\textbf{Metric} & \textbf{Value} \\",
            r"\midrule",
            f"Average TRACE Processing Time & {avg_proc_time:.2f} ms \\\\",
            f"Average Memory Consumption & {avg_mem:.2f} KB \\\\",
            f"Protocol Overhead (\%) & {avg_overhead:.2f}\% \\\\",
            f"Total Evaluated Task Executions & {total_tasks} \\\\",
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
        ]
        return "\n".join(lines)