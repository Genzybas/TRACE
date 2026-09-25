"""Framework-neutral recorder for observable agent execution events.

Adapters call ``record`` around observed planner, memory, tool, environment,
and action events. The recorder deliberately does not request private chain of
thought; payloads should contain only externally observable data permitted by
the experiment protocol.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from trace_eval.domain.primitives import EventCategory, ObservableEvidence
from trace_eval.domain.trace import BehaviourTrace


class TraceRecorder:
    """Collect an ordered BehaviourTrace for one real agent execution."""

    def __init__(self, trace_id: str, task_id: str, agent_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.trace_id = trace_id
        self.task_id = task_id
        self.agent_id = agent_id
        self.metadata = metadata or {}
        self._events: List[ObservableEvidence] = []

    def record(
        self,
        category: EventCategory,
        action_name: str,
        *,
        payload: Optional[Dict[str, Any]] = None,
        latency_ms: Optional[float] = None,
        is_error: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> ObservableEvidence:
        event = ObservableEvidence(
            event_id=str(uuid4()),
            timestamp=timestamp or datetime.now(timezone.utc),
            category=category,
            action_name=action_name,
            payload=payload or {},
            latency_ms=latency_ms,
            is_error=is_error,
            metadata=metadata or {},
        )
        self._events.append(event)
        return event

    def finalize(self) -> BehaviourTrace:
        return BehaviourTrace(
            trace_id=self.trace_id,
            task_id=self.task_id,
            agent_id=self.agent_id,
            events=tuple(self._events),
            metadata=self.metadata,
        )
