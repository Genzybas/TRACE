"""
Unit tests for TRACE BehaviourSignature and score calculations.
"""

import pytest
from pydantic import ValidationError

from trace_eval.assessment.signature import BehaviourSignature, GlobalCategoryWeights
from trace_eval.domain.profile import BehaviourProfile


def test_global_weights_validation():
    weights = GlobalCategoryWeights(alpha=0.5, beta=0.3, gamma=0.2)
    assert weights.alpha + weights.beta + weights.gamma == pytest.approx(1.0)

    with pytest.raises(ValidationError):
        GlobalCategoryWeights(alpha=0.5, beta=0.5, gamma=0.5)


def test_signature_and_score_computation():
    profile = BehaviourProfile(
        trace_id="tr_sig_1",
        agent_id="agent_1",
        cognitive=0.8,
        operational=0.7,
        reliability=0.9,
    )
    confidence = 0.5  # \kappa = 0.5

    sig = BehaviourSignature.create(profile, confidence)

    # S_TRACE = 0.4*0.8 + 0.3*0.7 + 0.3*0.9 = 0.32 + 0.21 + 0.27 = 0.80
    s_trace = sig.compute_trace_score()
    assert s_trace == pytest.approx(0.80)

    # S_Final = 0.5 * 0.80 = 0.40
    s_final = sig.compute_final_score()
    assert s_final == pytest.approx(0.40)