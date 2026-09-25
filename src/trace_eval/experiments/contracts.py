"""Validated contracts for reproducible TRACE experiments.

The manifest describes the experiment before execution. The JSONL run file
contains immutable, observable records produced by the evaluated agents. No
model calls or synthetic evidence are created by this module.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from trace_eval.domain.trace import BehaviourTrace


class TaskDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    task_id: str = Field(min_length=1)
    category: Literal["reasoning", "planning", "tool_assisted", "memory", "adaptive", "failure_recovery", "end_to_end"]
    objective: str = Field(min_length=1)
    version: str = Field(min_length=1)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    success_criterion: str = Field(min_length=1)


class AgentConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    agent_id: str = Field(min_length=1)
    provider: Literal["openai", "anthropic", "gemini", "qwen", "deepseek"]
    model_name: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    architecture: str = Field(min_length=1)
    api_key_env: str = Field(min_length=1)
    base_url: Optional[str] = None
    generation_parameters: Dict[str, Any] = Field(default_factory=dict)
    tools: List[str] = Field(default_factory=list)


class ExperimentManifest(BaseModel):
    """Pre-registered configuration required to reproduce a TRACE study."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    study_id: str = Field(min_length=1)
    protocol_version: str = Field(min_length=1)
    task_suite_version: str = Field(min_length=1)
    repeated_runs_per_condition: int = Field(ge=2)
    tasks: List[TaskDefinition] = Field(min_length=1)
    agents: List[AgentConfiguration] = Field(min_length=1)
    random_seeds: List[int] = Field(default_factory=list)
    environment: Dict[str, Any] = Field(default_factory=dict)
    normalization_bounds: Dict[str, Dict[str, float]] = Field(min_length=1)
    category_weights: Dict[str, float] = Field(default_factory=dict)
    global_weights: Dict[str, float] = Field(default_factory=dict)
    failure_handling: str = Field(min_length=1)

    @model_validator(mode="after")
    def unique_ids(self) -> "ExperimentManifest":
        task_ids = [task.task_id for task in self.tasks]
        agent_ids = [agent.agent_id for agent in self.agents]
        if len(task_ids) != len(set(task_ids)):
            raise ValueError("Task identifiers must be unique.")
        if len(agent_ids) != len(set(agent_ids)):
            raise ValueError("Agent identifiers must be unique.")
        for feature, bounds in self.normalization_bounds.items():
            if set(bounds) != {"min", "max"} or bounds["max"] <= bounds["min"]:
                raise ValueError(f"Normalization bounds for '{feature}' must contain min < max.")
        return self


class ExecutionRecord(BaseModel):
    """One completed or interrupted agent execution from a real task run."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str = Field(min_length=1)
    run_index: int = Field(ge=1)
    task_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    outcome: Literal["success", "partial", "failure", "interrupted"]
    success_score: float = Field(ge=0.0, le=1.0)
    agent_latency_ms: Optional[float] = Field(default=None, ge=0.0)
    trace: BehaviourTrace
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def trace_identity_matches_record(self) -> "ExecutionRecord":
        if self.trace.task_id != self.task_id or self.trace.agent_id != self.agent_id:
            raise ValueError("Record task_id and agent_id must match the embedded BehaviourTrace.")
        return self


class ValidationReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    expected_conditions: int
    observed_conditions: int
    expected_runs: int
    observed_runs: int
    missing_conditions: List[str] = Field(default_factory=list)
    unexpected_conditions: List[str] = Field(default_factory=list)
    duplicate_run_ids: List[str] = Field(default_factory=list)
    invalid_run_counts: Dict[str, int] = Field(default_factory=dict)

    @property
    def is_complete(self) -> bool:
        return (
            not self.missing_conditions
            and not self.unexpected_conditions
            and not self.duplicate_run_ids
            and not self.invalid_run_counts
        )
