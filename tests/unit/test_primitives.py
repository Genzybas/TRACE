"""
Unit tests for TRACE core domain primitives and evidence contracts.
"""

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from trace.domain.primitives import EventCategory, ObservableEvidence


def test_observable_evidence_instantiation():
    evidence = ObservableEvidence(
        event_id="evt_001",
        category=EventCategory.REASONING,
        action_name="thought_step",
        payload={"thought": "Decomposing task into subgoals."},
        latency_ms=120.5,
    )
    assert evidence.event_id == "evt_001"
    assert evidence.category == EventCategory.REASONING
    assert evidence.action_name == "thought_step"
    assert evidence.latency_ms == 120.5
    assert not evidence.is_error
    assert evidence.timestamp.tzinfo == timezone.utc


def test_observable_evidence_immutability():
    evidence = ObservableEvidence(
        event_id="evt_001",
        category=EventCategory.TOOL_USE,
        action_name="execute_sql",
    )
    with pytest.raises(ValidationError):
        evidence.action_name = "new_action"  # Immutable frozen object


def test_observable_evidence_invalid_latency():
    with pytest.raises(ValidationError):
        ObservableEvidence(
            event_id="evt_002",
            category=EventCategory.ACTION,
            action_name="invalid_latency",
            latency_ms=-10.0,  # Must be >= 0.0
        )


def test_timestamp_tz_conversion():
    naive_dt = datetime(2026, 3, 1, 12, 0, 0)
    evidence = ObservableEvidence(
        event_id="evt_003",
        category=EventCategory.SYSTEM,
        action_name="init",
        timestamp=naive_dt,
    )
    assert evidence.timestamp.tzinfo == timezone.utc