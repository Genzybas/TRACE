"""
Unit tests for TRACE BehaviourProfile and CategoryWeights.
"""

import pytest
from pydantic import ValidationError

from trace_eval.domain.profile import BehaviourProfile, CategoryWeights
from trace_eval.domain.vector import NormalizedBehaviourVector


def test_category_weights_valid_default():
    weights = CategoryWeights()
    assert weights.w_R + weights.w_P + weights.w_M == pytest.approx(1.0)
    assert weights.w_T + weights.w_E == pytest.approx(1.0)
    assert weights.w_A + weights.w_C == pytest.approx(1.0)


def test_category_weights_invalid_sum_raises_validation_error():
    with pytest.raises(ValidationError):
        CategoryWeights(w_R=0.5, w_P=0.5, w_M=0.5)  # Sums to 1.5


def test_behaviour_profile_from_normalized_vector():
    norm_vector = NormalizedBehaviourVector(
        trace_id="tr_p1",
        agent_id="agent_alpha",
        normalized_features={
            "D_R_reasoning_ratio": 0.8,
            "D_P_planning_ratio": 0.6,
            "D_M_memory_ratio": 0.5,
            "D_T_tool_success_rate": 0.9,
            "D_E_execution_speed": 0.7,
            "D_A_adaptability_score": 0.4,
            "D_C_error_free_rate": 1.0,
        },
    )

    profile = BehaviourProfile.from_normalized_vector(norm_vector)

    # C = 0.4*0.8 + 0.4*0.6 + 0.2*0.5 = 0.32 + 0.24 + 0.10 = 0.66
    assert profile.cognitive == pytest.approx(0.66)
    # O = 0.6*0.9 + 0.4*0.7 = 0.54 + 0.28 = 0.82
    assert profile.operational == pytest.approx(0.82)
    # R = 0.5*0.4 + 0.5*1.0 = 0.20 + 0.50 = 0.70
    assert profile.reliability == pytest.approx(0.70)
    assert profile.to_tuple() == (pytest.approx(0.66), pytest.approx(0.82), pytest.approx(0.70))
    