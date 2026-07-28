"""
BehaviourProfile Domain Model for TRACE.

Implements hierarchical category aggregation converting normalized behavioural
dimensions into Cognitive (C), Operational (O), and Reliability (R) scores.

Manuscript Definitions:
    C = w_R * D_R + w_P * D_P + w_M * D_M,  where w_R + w_P + w_M = 1
    O = w_T * D_T + w_E * D_E,              where w_T + w_E = 1
    R = w_A * D_A + w_C * D_C,              where w_A + w_C = 1
    BP = (C, O, R)
"""

from typing import Dict, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from trace.domain.vector import NormalizedBehaviourVector


class CategoryWeights(BaseModel):
    """
    Weighting configuration for TRACE behavioural categories.
    Enforces that intra-category dimension weights sum to exactly 1.0.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    # Cognitive category weights
    w_R: float = Field(default=0.4, ge=0.0, le=1.0, description="Weight for Reasoning (D_R)")
    w_P: float = Field(default=0.4, ge=0.0, le=1.0, description="Weight for Planning (D_P)")
    w_M: float = Field(default=0.2, ge=0.0, le=1.0, description="Weight for Memory (D_M)")

    # Operational category weights
    w_T: float = Field(default=0.6, ge=0.0, le=1.0, description="Weight for Tool Use (D_T)")
    w_E: float = Field(default=0.4, ge=0.0, le=1.0, description="Weight for Efficiency (D_E)")

    # Reliability category weights
    w_A: float = Field(default=0.5, ge=0.0, le=1.0, description="Weight for Adaptability (D_A)")
    w_C: float = Field(default=0.5, ge=0.0, le=1.0, description="Weight for Consistency (D_C)")

    @field_validator("w_M")
    @classmethod
    def validate_cognitive_sum(cls, v: float, info) -> float:
        w_R = info.data.get("w_R", 0.4)
        w_P = info.data.get("w_P", 0.4)
        total = w_R + w_P + v
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Cognitive weights (w_R, w_P, w_M) must sum to 1.0, got {total}")
        return v

    @field_validator("w_E")
    @classmethod
    def validate_operational_sum(cls, v: float, info) -> float:
        w_T = info.data.get("w_T", 0.6)
        total = w_T + v
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Operational weights (w_T, w_E) must sum to 1.0, got {total}")
        return v

    @field_validator("w_C")
    @classmethod
    def validate_reliability_sum(cls, v: float, info) -> float:
        w_A = info.data.get("w_A", 0.5)
        total = w_A + v
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Reliability weights (w_A, w_C) must sum to 1.0, got {total}")
        return v


class BehaviourProfile(BaseModel):
    """
    Structured domain assessment obtained by aggregating behavioural dimensions
    into higher-level behavioural categories.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
    )

    trace_id: str = Field(..., description="ID of source trace.", min_length=1)
    agent_id: str = Field(..., description="ID of evaluated agent.", min_length=1)
    cognitive: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Cognitive Behaviour score C combining reasoning, planning, memory.",
    )
    operational: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Operational Behaviour score O combining tool use and efficiency.",
    )
    reliability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Reliability Behaviour score R combining adaptability and consistency.",
    )

    @classmethod
    def from_normalized_vector(
        cls,
        norm_vector: NormalizedBehaviourVector,
        weights: Optional[CategoryWeights] = None,
    ) -> "BehaviourProfile":
        """
        Aggregate a NormalizedBehaviourVector into a BehaviourProfile using CategoryWeights.
        """
        weights = weights or CategoryWeights()
        nf = norm_vector.normalized_features

        # Extract dimensions, falling back to 0.0 if not explicit
        d_R = nf.get("D_R_reasoning_ratio", 0.0)
        d_P = nf.get("D_P_planning_ratio", 0.0)
        d_M = nf.get("D_M_memory_ratio", 0.0)

        d_T = nf.get("D_T_tool_success_rate", 0.0)
        d_E = nf.get("D_E_execution_speed", 0.0)

        d_A = nf.get("D_A_adaptability_score", 0.0)
        d_C = nf.get("D_C_error_free_rate", 0.0)

        c_score = max(0.0, min(1.0, weights.w_R * d_R + weights.w_P * d_P + weights.w_M * d_M))
        o_score = max(0.0, min(1.0, weights.w_T * d_T + weights.w_E * d_E))
        r_score = max(0.0, min(1.0, weights.w_A * d_A + weights.w_C * d_C))

        return cls(
            trace_id=norm_vector.trace_id,
            agent_id=norm_vector.agent_id,
            cognitive=c_score,
            operational=o_score,
            reliability=r_score,
        )

    def to_tuple((self)) -> tuple[float, float, float]:
        """Return profile scores as a (C, O, R) tuple."""
        return (self.cognitive, self.operational, self.reliability)