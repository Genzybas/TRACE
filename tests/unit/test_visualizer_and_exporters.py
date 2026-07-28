"""
Unit tests for TRACE Visualization utilities and Multi-Format Exporters.
"""

from datetime import datetime, timezone
import os
import tempfile

from trace.domain.primitives import EventCategory, ObservableEvidence
from trace.domain.trace import BehaviourTrace
from trace.experiments.exporters_multi import MultiFormatExporter
from trace.experiments.runner import ExperimentRunner
from trace.experiments.visualizer import TRACEVisualizer


def test_visualizer_and_multi_exporters():
    t0 = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
    events = [
        ObservableEvidence(
            event_id="e1",
            timestamp=t0,
            category=EventCategory.PLANNING,
            action_name="plan",
            latency_ms=100.0,
        )
    ]
    trace = BehaviourTrace(trace_id="t1", task_id="task_1", agent_id="Agent_A", events=events)

    runner = ExperimentRunner()
    result = runner.run_agent_experiment("Agent_A", [trace], [True], [0.1])

    # Test CSV Export
    csv_out = MultiFormatExporter.export_to_csv([result])
    assert "Agent_A" in csv_out
    assert "Cognitive_C" in csv_out

    # Test Markdown Export
    md_out = MultiFormatExporter.export_to_markdown([result])
    assert "| **Agent_A** |" in md_out

    # Test Plot Generation
    with tempfile.TemporaryDirectory() as tmpdir:
        radar_path = os.path.join(tmpdir, "radar.png")
        bar_path = os.path.join(tmpdir, "bar.png")

        TRACEVisualizer.plot_behavioural_radar([result], output_path=radar_path)
        TRACEVisualizer.plot_score_vs_success_bar([result], output_path=bar_path)

        assert os.path.exists(radar_path)
        assert os.path.exists(bar_path)