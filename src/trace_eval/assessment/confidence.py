"""
Behavioural Confidence Estimator for TRACE.

Implements exponential stability modeling to quantify behavioural consistency across
repeated task executions.

Manuscript Definitions:
    \bar{BV} = (1/N) * \sum BV^{(i)}
    \sigma_B = \sqrt{ (1/N) * \sum || BV^{(i)} - \bar{BV} ||_2^2 }
    \kappa = S_B = \exp(-\lambda * \sigma_B),  where \kappa \in (0, 1]
"""

import math
from typing import Sequence
import numpy as np
from pydantic import BaseModel, ConfigDict, Field, field_validator

from trace_eval.domain.vector import BehaviourVector


class BehaviourConfidenceEstimator(BaseModel):
    """
    Estimator computing Behavioural Confidence \kappa over N repeated executions.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    lambda_sensitivity: float = Field(
        default=1.0,
        gt=0.0,
        description=r"Sensitivity scaling parameter \lambda > 0 controlling exponential decay rate.",
    )

    def compute_confidence(self, vectors: Sequence[BehaviourVector]) -> float:
        """
        Compute \kappa given N BehaviourVectors from repeated task runs.

        Returns 1.0 if N <= 1 (insufficient variability sample).
        """
        if len(vectors) <= 1:
            return 1.0

        # Extract set of common keys present across all vectors
        feature_keys = sorted(list(vectors[0].features.keys()))
        matrix = []

        for vec in vectors:
            row = [vec.features.get(k, 0.0) for k in feature_keys]
            matrix.append(row)

        data = np.array(matrix, dtype=np.float64)  # Shape: (N, num_features)
        mean_vector = np.mean(data, axis=0)        # Shape: (num_features,)

        # Compute Euclidean distance of each vector from mean_vector
        diffs = data - mean_vector
        squared_euclidean_dists = np.sum(diffs ** 2, axis=1)

        # \sigma_B = \sqrt{ (1/N) * \sum || BV^{(i)} - \bar{BV} ||_2^2 }
        sigma_B = math.sqrt(float(np.mean(squared_euclidean_dists)))

        # \kappa = \exp(-\lambda * \sigma_B)
        kappa = math.exp(-self.lambda_sensitivity * sigma_B)

        # Enforce bounded domain (0, 1]
        return max(1e-6, min(1.0, kappa))