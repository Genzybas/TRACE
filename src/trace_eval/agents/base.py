from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, Sequence
from trace_eval.domain.primitives import EventCategory
from trace_eval.experiments.recorder import TraceRecorder
@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable[..., Any]
    category: EventCategory = EventCategory.TOOL_USE
@dataclass(frozen=True)
class AgentReply:
    text: str
    metadata: Dict[str, Any]
class AgentAdapter(ABC):
    def __init__(self, agent_id: str, model: str, temperature: float = 0.0):
        self.agent_id, self.model, self.temperature = agent_id, model, temperature
    @abstractmethod
    def run(self, *, task_id: str, prompt: str, recorder: TraceRecorder, tools: Sequence[ToolSpec], max_turns: int = 12) -> AgentReply: ...
    @staticmethod
    def _record_final(recorder: TraceRecorder, text: str) -> None:
        recorder.record(EventCategory.ACTION, "submit_answer", payload={"answer": text[:4000]})
