"""
Unit tests for TRACE BehaviourVector domain models and normalization logic.
"""

import pytest
from pydantic import ValidationError

from trace.domain.vector import BehaviourVector, NormalizedBehaviourVector


def test_behaviour_vector_creation():
    bv = BehaviourVector(
        trace_id="tr_001",
        agent_id="agent_a",
        features={"reasoning_depth": 4.0, "error_count": 0.0},
    )
    assert bv.trace_id == "tr_001"
    assert bv["reasoning_depth"] == 4.0


def test_empty_features_raises_validation_error():
    with pytest.raises(ValidationError):
        BehaviourVector(
            trace_id="tr_001",
            agent_id="agent_a",
            features={},
        )


def test_min_max_normalization():
    bv = BehaviourVector(
        trace_id="tr_002",
        agent_id="agent_a",
        features={"reasoning_depth": 5.0, "latency_sec": 10.0},
    )
    min_bounds = {"reasoning_depth": 0.0, "latency_sec": 0.0}
    max_bounds = {"reasoning_depth": 10.0, "latency_sec": 20.0}

    norm_bv = bv.normalize(min_bounds, max_bounds)
    assert isinstance(norm_bv, NormalizedBehaviourVector)
    assert norm_bv["reasoning_depth"] == 0.5
    assert norm_bv["latency_sec"] == 0.5


def test_invalid_normalization_bounds():
    bv = BehaviourVector(
        trace_id="tr_003",
        agent_id="agent_a",
        features={"score": 5.0},
    )
    with pytest.raises(ValueError):
        bv.normalize(min_bounds={"score": 10.0}, max_bounds={"score": 5.0})


def test_clamping_out_of_bounds_values():
    bv = BehaviourVector(
        trace_id="tr_004",
        agent_id="agent_a",
        features={"val": 15.0},
    )
    norm_bv = bv.normalize(min_bounds={"val": 0.0}, max_bounds={"val": 10.0})
    assert norm_bv["val"] == 1.0  # Clamped to upper bound 1.0