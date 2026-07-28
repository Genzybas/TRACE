"""
Unit tests for TRACE Behavioural Confidence estimation.
"""

import math
import pytest

from trace.assessment.confidence import BehaviourConfidenceEstimator
from trace.domain.vector import BehaviourVector


def test_confidence_identical_vectors_returns_one():
    v1 = BehaviourVector(trace_id="t1", agent_id="a1", features={"f1": 1.0, "f2": 2.0})
    v2 = BehaviourVector(trace_id="t2", agent_id="a1", features={"f1": 1.0, "f2": 2.0})

    estimator = BehaviourConfidenceEstimator(lambda_sensitivity=1.0)
    kappa = estimator.compute_confidence([v1, v2])
    assert kappa == pytest.approx(1.0)


def test_confidence_exponential_decay():
    v1 = BehaviourVector(trace_id="t1", agent_id="a1", features={"f1": 0.0})
    v2 = BehaviourVector(trace_id="t2", agent_id="a1", features={"f1": 2.0})

    # Mean = 1.0. Diffs = [-1.0, 1.0]. Squared diffs = [1.0, 1.0].
    # Mean sq diff = 1.0. \sigma_B = sqrt(1.0) = 1.0.
    # \kappa = exp(-1.0 * 1.0) = 1 / e \approx 0.367879

    estimator = BehaviourConfidenceEstimator(lambda_sensitivity=1.0)
    kappa = estimator.compute_confidence([v1, v2])
    assert kappa == pytest.approx(math.exp(-1.0))


def test_confidence_single_vector_defaults_to_one():
    v1 = BehaviourVector(trace_id="t1", agent_id="a1", features={"f1": 1.0})
    estimator = BehaviourConfidenceEstimator()
    assert estimator.compute_confidence([v1]) == 1.0