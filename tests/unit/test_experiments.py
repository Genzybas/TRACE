"""
Unit tests for TRACE Experiment Runner and LaTeX Exporter.
"""

from datetime import datetime, timedelta, timezone
from trace_eval.domain.primitives import EventCategory, ObservableEvidence
from trace_eval.domain.trace import BehaviourTrace
from trace_eval.experiments.exporter import LaTeXExporter
from trace_eval.experiments.runner import ExperimentRunner


def test_experiment_runner_and_exporter():
    t0 = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
    events = [
        ObservableEvidence(
            event_id="e1",
            timestamp=t0,
            category=EventCategory.PLANNING,
            action_name="plan",
            latency_ms=100.0,
        ),
        ObservableEvidence(
            event_id="e2",
            timestamp=t0 + timedelta(milliseconds=100),
            category=EventCategory.REASONING,
            action_name="think",
            latency_ms=150.0,
        ),
    ]
    trace = BehaviourTrace(trace_id="t1", task_id="task_1", agent_id="GPT-5_Agent", events=events)

    runner = ExperimentRunner()
    result = runner.run_agent_experiment(
        agent_id="GPT-5_Agent",
        traces=[trace, trace],
        task_successes=[True, True],
        agent_latencies_sec=[0.25, 0.25],
    )

    assert result.agent_id == "GPT-5_Agent"
    assert result.task_success_rate == 100.0
    assert result.avg_latency_sec == 0.25

    table_3_latex = LaTeXExporter.export_table_3_characterization([result])
    assert "GPT-5_Agent" in table_3_latex
    assert r"\begin{table}" in table_3_latex

    table_7_latex = LaTeXExporter.export_table_7_computational([result])
    assert "Average TRACE Processing Time" in table_7_latex