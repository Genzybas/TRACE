"""
End-to-End Integration tests verifying the complete TRACE pipeline.
"""

from datetime import datetime, timedelta, timezone
from trace_eval.domain.primitives import EventCategory, ObservableEvidence
from trace_eval.domain.trace import BehaviourTrace
from trace_eval.pipeline import TRACEPipeline


def test_full_pipeline_execution():
    t0 = datetime(2026, 3, 1, 12, 0, 0, tzinfo=timezone.utc)

    # Run 1
    events_1 = [
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
            category=EventCategory.TOOL_USE,
            action_name="query",
            latency_ms=200.0,
        ),
    ]
    trace_1 = BehaviourTrace(
        trace_id="tr_1", task_id="task_1", agent_id="agent_alpha", events=events_1
    )

    # Run 2 (Identical run for high confidence)
    events_2 = [
        ObservableEvidence(
            event_id="e3",
            timestamp=t0,
            category=EventCategory.PLANNING,
            action_name="plan",
            latency_ms=100.0,
        ),
        ObservableEvidence(
            event_id="e4",
            timestamp=t0 + timedelta(milliseconds=100),
            category=EventCategory.TOOL_USE,
            action_name="query",
            latency_ms=200.0,
        ),
    ]
    trace_2 = BehaviourTrace(
        trace_id="tr_2", task_id="task_1", agent_id="agent_alpha", events=events_2
    )

    pipeline = TRACEPipeline()
    signature = pipeline.evaluate_agent_runs([trace_1, trace_2])

    assert signature.agent_id == "agent_alpha"
    assert signature.confidence == 1.0  # Identical runs yield kappa = 1.0
    assert signature.compute_trace_score() > 0.0
    assert signature.compute_final_score() == signature.compute_trace_score()