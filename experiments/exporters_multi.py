"""
Multi-Format Results Exporter for TRACE.

Exports benchmark experiment results into CSV and Markdown formats.
"""

import csv
import io
from typing import List

from trace.experiments.runner import ExperimentResult


class MultiFormatExporter:
    """Exports ExperimentResults to CSV and Markdown tables."""

    @staticmethod
    def export_to_csv(results: List[ExperimentResult]) -> str:
        """Export benchmark evaluation results to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(
            [
                "Agent_ID",
                "Cognitive_C",
                "Operational_O",
                "Reliability_R",
                "Confidence_Kappa",
                "S_TRACE",
                "S_Final",
                "Task_Success_Rate_Pct",
                "Avg_Latency_Sec",
                "Processing_Time_Ms",
                "Protocol_Overhead_Pct",
            ]
        )

        for res in results:
            sig = res.signature
            writer.writerow(
                [
                    res.agent_id,
                    f"{sig.cognitive:.4f}",
                    f"{sig.operational:.4f}",
                    f"{sig.reliability:.4f}",
                    f"{sig.confidence:.4f}",
                    f"{sig.compute_trace_score():.4f}",
                    f"{sig.compute_final_score():.4f}",
                    f"{res.task_success_rate:.2f}",
                    f"{res.avg_latency_sec:.4f}",
                    f"{res.processing_time_ms:.2f}",
                    f"{res.protocol_overhead_pct:.2f}",
                ]
            )

        return output.getvalue()

    @staticmethod
    def export_to_markdown(results: List[ExperimentResult]) -> str:
        """Export benchmark evaluation results to Markdown table format."""
        lines = [
            "| Agent ID | Cognitive (C) | Operational (O) | Reliability (R) | Confidence ($\kappa$) | $S_{Final}$ | Task Success (%) | Avg Latency (s) |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
        ]

        for res in results:
            sig = res.signature
            lines.append(
                f"| **{res.agent_id}** | {sig.cognitive:.3f} | {sig.operational:.3f} | "
                f"{sig.reliability:.3f} | {sig.confidence:.3f} | **{sig.compute_final_score():.3f}** | "
                f"{res.task_success_rate:.1f}% | {res.avg_latency_sec:.2f}s |"
            )

        return "\n".join(lines)