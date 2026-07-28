"""
Unit tests for TRACE BehaviourTrace domain aggregate.
"""

from datetime import datetime, timedelta, timezone
import pytest
from pydantic import ValidationError

from trace.domain.primitives import EventCategory, ObservableEvidence
from trace.domain.trace import BehaviourTrace


@pytest.fixture
def sample_events():
    t0 = datetime(2026, 3, 1, 10, 0, 0, tzinfo=timezone.utc)
    return [
        ObservableEvidence(
            event_id="e1",
            timestamp=t0,
            category=EventCategory.PLANNING,
            action_name="decompose_task",
            latency_ms=50.0,
        ),
        ObservableEvidence(
            event_id="e2",
            timestamp=t0 + timedelta(seconds=1),
            category=EventCategory.TOOL_USE,
            action_name="run_query",
            latency_ms=150.0,
            is_error=True,
        ),
        ObservableEvidence(
            event_id="e3",
            timestamp=t0 + timedelta(seconds=2),
            category=EventCategory.REASONING,
            action_name="evaluate_result",
            latency_ms=80.0,
        ),
    ]


def test_behaviour_trace_instantiation(sample_events):
    trace = BehaviourTrace(
        trace_id="tr_100",
        task_id="task_01",
        agent_id="agent_alpha",
        events=sample_events,
    )
    assert len(trace) == 3
    assert trace.trace_id == "tr_100"
    assert trace.total_duration_ms == 280.0
    assert pytest.approx(trace.error_rate) == 1.0 / 3.0


def test_out_of_order_events_raise_validation_error():
    t0 = datetime(2026, 3, 1, 10, 0, 0, tzinfo=timezone.utc)
    e1 = ObservableEvidence(
        event_id="e1",
        timestamp=t0 + timedelta(seconds=5),
        category=EventCategory.REASONING,
        action_name="later_step",
    )
    e2 = ObservableEvidence(
        event_id="e2",
        timestamp=t0,
        category=EventCategory.REASONING,
        action_name="earlier_step",
    )
    with pytest.raises(ValidationError):
        BehaviourTrace(
            trace_id="tr_invalid",
            task_id="task_01",
            agent_id="agent_alpha",
            events=[e1, e2],
        )


def test_behaviour_trace_filtering(sample_events):
    trace = BehaviourTrace(
        trace_id="tr_101",
        task_id="task_01",
        agent_id="agent_alpha",
        events=sample_events,
    )
    tool_events = trace.filter_by_category(EventCategory.TOOL_USE)
    assert len(tool_events) == 1
    assert tool_events[0].event_id == "e2"

    error_events = trace.filter_by_errors()
    assert len(error_events) == 1
    assert error_events[0].event_id == "e2"