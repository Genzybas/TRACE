"""
BehaviourVector Domain Model for TRACE.

Defines feature representations, normalization logic, and dimension mapping 
derived from BehaviourTraces in the Behaviour Interpretation Layer.

Manuscript Definitions:
    BV = (b_1, b_2, ..., b_m)
    \hat{b}_i = (b_i - b_i^{\min}) / (b_i^{\max} - b_i^{\min})
    \hat{BV} = (\hat{b}_1, \hat{b}_2, ..., \hat{b}_m)
"""

from typing import Dict, List, Mapping, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class BehaviourVector(BaseModel):
    """
    Unnormalized raw feature vector extracted from a BehaviourTrace.

    Contains quantitative metrics derived across reasoning, planning, memory,
    tool usage, efficiency, adaptability, and consistency.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
    )

    trace_id: str = Field(..., description="ID of source BehaviourTrace.", min_length=1)
    agent_id: str = Field(..., description="ID of evaluated agent.", min_length=1)
    features: Dict[str, float] = Field(
        ...,
        description="Dictionary mapping feature names b_i to raw numeric values.",
    )

    @field_validator("features")
    @classmethod
    def validate_non_empty(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Ensure feature dictionary contains at least one extracted feature."""
        if not v:
            raise ValueError("BehaviourVector features dictionary cannot be empty.")
        return v

    def __getitem__(self, feature_name: str) -> float:
        """Access raw feature value b_i by name."""
        return self.features[feature_name]

    def normalize(
        self,
        min_bounds: Mapping[str, float],
        max_bounds: Mapping[str, float],
    ) -> "NormalizedBehaviourVector":
        """
        Normalize feature vector to [0, 1] using explicit domain bounds.

        \hat{b}_i = (b_i - b_i^{\min}) / (b_i^{\max} - b_i^{\min})
        """
        normalized_features: Dict[str, float] = {}

        for name, value in self.features.items():
            b_min = min_bounds.get(name, 0.0)
            b_max = max_bounds.get(name, 1.0)

            if b_max <= b_min:
                raise ValueError(
                    f"Invalid normalization bounds for feature '{name}': "
                    f"max ({b_max}) must be greater than min ({b_min})."
                )

            # Min-Max Scaling clipped to [0, 1] range
            norm_val = (value - b_min) / (b_max - b_min)
            clamped_val = max(0.0, min(1.0, norm_val))
            normalized_features[name] = clamped_val

        return NormalizedBehaviourVector(
            trace_id=self.trace_id,
            agent_id=self.agent_id,
            normalized_features=normalized_features,
        )


class NormalizedBehaviourVector(BaseModel):
    """
    Normalized feature vector where all feature values \hat{b}_i \in [0, 1].
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
    )

    trace_id: str = Field(..., description="ID of source BehaviourTrace.", min_length=1)
    agent_id: str = Field(..., description="ID of evaluated agent.", min_length=1)
    normalized_features: Dict[str, float] = Field(
        ...,
        description="Normalized features \hat{b}_i strictly bounded in [0.0, 1.0].",
    )

    @field_validator("normalized_features")
    @classmethod
    def validate_bounds(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Verify that all normalized values reside within [0, 1]."""
        if not v:
            raise ValueError("NormalizedBehaviourVector cannot be empty.")
        for name, val in v.items():
            if not (0.0 <= val <= 1.0):
                raise ValueError(
                    f"Normalized feature '{name}' value {val} out of bounds [0, 1]."
                )
        return v

    def __getitem__(self, feature_name: str) -> float:
        """Access normalized feature value \hat{b}_i by name."""
        return self.normalized_features[feature_name]