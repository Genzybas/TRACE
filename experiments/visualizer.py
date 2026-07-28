"""
TRACE Visualization Utilities.

Generates plots (Radar charts, Bar plots) to visualize Behavioural Signatures,
category breakdowns, and performance vs. confidence comparisons.
"""

from typing import List, Optional
import matplotlib.pyplot as plt
import numpy as np

from trace.experiments.runner import ExperimentResult


class TRACEVisualizer:
    """Utility for generating TRACE evaluation figures and charts."""

    @staticmethod
    def plot_behavioural_radar(
        results: List[ExperimentResult],
        output_path: Optional[str] = None,
    ) -> None:
        """
        Generates a publication-grade Radar (Spider) chart comparing agent
        Behaviour Profiles (Cognitive, Operational, Reliability) and Confidence.
        """
        labels = ["Cognitive (C)", "Operational (O)", "Reliability (R)", "Confidence (\u03ba)"]
        num_vars = len(labels)

        # Compute angle for each axis
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]  # Complete circle loop

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

        for res in results:
            sig = res.signature
            values = [sig.cognitive, sig.operational, sig.reliability, sig.confidence]
            values += values[:1]  # Complete loop
            ax.plot(angles, values, linewidth=2, linestyle="solid", label=res.agent_id)
            ax.fill(angles, values, alpha=0.15)

        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        plt.xticks(angles[:-1], labels, color="black", size=11)
        ax.set_rlabel_position(0)
        plt.yticks([0.2, 0.4, 0.6, 0.8, 1.0], ["0.2", "0.4", "0.6", "0.8", "1.0"], color="grey", size=9)
        plt.ylim(0, 1)

        plt.title("TRACE Behavioural Signature Comparison", size=14, y=1.08)
        plt.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
        else:
            plt.show()
        plt.close()

    @staticmethod
    def plot_score_vs_success_bar(
        results: List[ExperimentResult],
        output_path: Optional[str] = None,
    ) -> None:
        """
        Bar chart comparing conventional Task Success Rate against TRACE Final Score.
        """
        agents = [r.agent_id for r in results]
        tsr = [r.task_success_rate / 100.0 for r in results]
        final_scores = [r.signature.compute_final_score() for r in results]

        x = np.arange(len(agents))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x - width / 2, tsr, width, label="Task Success Rate (Normalized)", color="#4C72B0")
        ax.bar(x + width / 2, final_scores, width, label="TRACE Final Score (S_Final)", color="#55A868")

        ax.set_ylabel("Score / Normalized Rate")
        ax.set_title("Conventional Task Success Rate vs. TRACE Confidence-Aware Score")
        ax.set_xticks(x)
        ax.set_xticklabels(agents, rotation=15, ha="right")
        ax.set_ylim(0, 1.1)
        ax.legend()
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        plt.tight_layout()

        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
        else:
            plt.show()
        plt.close()