"""
BehaviourTrace Domain Aggregate for TRACE.

Defines the BehaviourTrace domain entity representing an ordered sequence of
ObservableEvidence events collected during an agent's task execution.

Manuscript Definition:
    BT = (e_1, e_2, ..., e_n)
"""

from typing import Any, Dict, Iterator, List, Optional, Sequence
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .primitives import EventCategory, ObservableEvidence


class BehaviourTrace(BaseModel):
    """
    Domain Aggregate representing an ordered sequence of execution events.

    Guarantees strict chronological ordering and immutability over recorded
    ObservableEvidence instances for a specific execution run.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=True,
    )

    trace_id: str = Field(
        ...,
        description="Unique identifier for the behaviour trace.",
        min_length=1,
    )
    task_id: str = Field(
        ...,
        description="Identifier of the task performed during this trace.",
        min_length=1,
    )
    agent_id: str = Field(
        ...,
        description="Identifier of the LLM agent evaluated.",
        min_length=1,
    )
    events: Sequence[ObservableEvidence] = Field(
        default_factory=tuple,
        description="Chronologically ordered sequence of observable execution events (e_1, e_2, ..., e_n).",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Global trace metadata (environment setup, parameters, model configuration).",
    )

    @field_validator("events")
    @classmethod
    def validate_chronological_order(
        cls, v: Sequence[ObservableEvidence]
    ) -> Sequence[ObservableEvidence]:
        """Ensure that recorded events are strictly sorted chronologically."""
        if len(v) <= 1:
            return v
        for i in range(1, len(v)):
            if v[i].timestamp < v[i - 1].timestamp:
                raise ValueError(
                    f"Execution events are out of chronological order at index {i}: "
                    f"{v[i - 1].timestamp} > {v[i].timestamp}"
                )
        return v

    def __len__(self) -> int:
        """Return total event count n."""
        return len(self.events)

    def __getitem__(self, index: int) -> ObservableEvidence:
        """Access execution event e_i by index."""
        return self.events[index]

    def __iter__(self) -> Iterator[ObservableEvidence]:
        """Iterate chronologically over recorded execution events."""
        return iter(self.events)

    def filter_by_category(self, category: EventCategory) -> List[ObservableEvidence]:
        """Extract subset of events belonging to a specific category."""
        return [e for e in self.events if e.category == category]

    def filter_by_errors(self) -> List[ObservableEvidence]:
        """Extract subset of events that encountered execution errors."""
        return [e for e in self.events if e.is_error]

    @property
    def total_duration_ms(self) -> float:
        """Compute aggregate execution duration in milliseconds from recorded event latencies."""
        return sum(e.latency_ms for e in self.events if e.latency_ms is not None)

    @property
    def error_rate(self) -> float:
        """Compute proportion of execution events that produced errors."""
        if not self.events:
            return 0.0
        return len(self.filter_by_errors()) / len(self.events)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize trace aggregate to dictionary."""
        return self.model_dump(mode="json")