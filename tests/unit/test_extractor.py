"""
Unit tests for TRACE feature extraction logic.
"""
from datetime import datetime, timedelta, timezone
import pytest

from trace_eval.domain.primitives import EventCategory, ObservableEvidence
from trace_eval.domain.trace import BehaviourTrace
from trace_eval.interpretation.extractor import DefaultBehaviourFeatureExtractor


def test_extractor_feature_derivation():
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
            category=EventCategory.TOOL_USE,
            action_name="query",
            latency_ms=200.0,
            is_error=True,
        ),
        ObservableEvidence(
            event_id="e3",
            timestamp=t0 + timedelta(milliseconds=300),
            category=EventCategory.REASONING,
            action_name="recover",
            latency_ms=100.0,
        ),
    ]
    trace = BehaviourTrace(
        trace_id="tr_ext_1",
        task_id="task_1",
        agent_id="agent_1",
        events=events,
    )

    extractor = DefaultBehaviourFeatureExtractor()
    bv = extractor.extract(trace)

    assert bv["D_P_planning_ratio"] == pytest.approx(1.0 / 3.0)
    assert bv["D_R_reasoning_ratio"] == pytest.approx(1.0 / 3.0)
    assert bv["D_T_tool_success_rate"] == 0.0
    assert bv["D_A_adaptability_score"] == 1.0  # Recovered from e2 error at e3
    assert bv["D_C_error_free_rate"] == pytest.approx(2.0 / 3.0)