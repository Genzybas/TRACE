"""
Behaviour Interpretation Extractor for TRACE.

Implements feature extraction routines transforming a BehaviourTrace into a
BehaviourVector.

Manuscript Definition:
    BV = \Phi(BT)
"""

from abc import ABC, abstractmethod
from typing import Dict, List

from trace_eval.domain.primitives import EventCategory
from trace_eval.domain.trace import BehaviourTrace
from trace_eval.domain.vector import BehaviourVector


class BaseFeatureExtractor(ABC):
    """Abstract interface for feature extractors mapping BT -> BV."""

    @abstractmethod
    def extract(self, trace: BehaviourTrace) -> BehaviourVector:
        """Extract a BehaviourVector from an input BehaviourTrace."""
        pass


class DefaultBehaviourFeatureExtractor(BaseFeatureExtractor):
    """
    Standard production feature extractor for TRACE.

    Derives quantitative metrics across Reasoning, Planning, Memory, Tool Use,
    Execution Efficiency, Adaptability, and Consistency.
    """

    def extract(self, trace: BehaviourTrace) -> BehaviourVector:
        """Extract domain features D_R, D_P, D_M, D_T, D_E, D_A, D_C features."""
        events = trace.events
        total_events = len(events)

        if total_events == 0:
            features = {
                "D_R_reasoning_ratio": 0.0,
                "D_P_planning_ratio": 0.0,
                "D_M_memory_ratio": 0.0,
                "D_T_tool_success_rate": 0.0,
                "D_E_execution_speed": 0.0,
                "D_A_adaptability_score": 0.0,
                "D_C_error_free_rate": 1.0,
            }
            return BehaviourVector(
                trace_id=trace.trace_id,
                agent_id=trace.agent_id,
                features=features,
            )

        reasoning_events = trace.filter_by_category(EventCategory.REASONING)
        planning_events = trace.filter_by_category(EventCategory.PLANNING)
        memory_events = trace.filter_by_category(EventCategory.MEMORY)
        tool_events = trace.filter_by_category(EventCategory.TOOL_USE)
        error_events = trace.filter_by_errors()

        tool_success_rate = (
            (len(tool_events) - sum(1 for e in tool_events if e.is_error)) / len(tool_events)
            if tool_events
            else 1.0
        )

        total_latency_sec = trace.total_duration_ms / 1000.0
        execution_speed = (
            total_events / total_latency_sec if total_latency_sec > 0 else 1.0
        )

        # Recovery metric: count errors that were followed by non-error steps
        recovery_count = 0
        for i, event in enumerate(events[:-1]):
            if event.is_error and not events[i + 1].is_error:
                recovery_count += 1
        adaptability_score = (
            recovery_count / len(error_events) if error_events else 1.0
        )

        features = {
            "D_R_reasoning_ratio": len(reasoning_events) / total_events,
            "D_P_planning_ratio": len(planning_events) / total_events,
            "D_M_memory_ratio": len(memory_events) / total_events,
            "D_T_tool_success_rate": tool_success_rate,
            "D_E_execution_speed": execution_speed,
            "D_A_adaptability_score": adaptability_score,
            "D_C_error_free_rate": 1.0 - trace.error_rate,
        }

        return BehaviourVector(
            trace_id=trace.trace_id,
            agent_id=trace.agent_id,
            features=features,
        )