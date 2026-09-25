"""Condition-level TRACE analysis, uncertainty summaries, and audit checks."""

from __future__ import annotations

from collections import Counter, defaultdict
from math import sqrt
from statistics import mean, stdev
from time import perf_counter
import tracemalloc
from typing import Dict, List, Sequence, Tuple

from pydantic import BaseModel, ConfigDict

from trace_eval.assessment.signature import BehaviourSignature
from trace_eval.assessment.confidence import BehaviourConfidenceEstimator
from trace_eval.domain.profile import CategoryWeights
from trace_eval.assessment.signature import GlobalCategoryWeights
from trace_eval.experiments.contracts import ExecutionRecord, ExperimentManifest, ValidationReport
from trace_eval.pipeline import TRACEPipeline


def _mean_ci(values: Sequence[float]) -> Tuple[float, float, float]:
    """Return a mean and normal-approximation 95% confidence interval."""
    if not values:
        raise ValueError("Cannot summarize an empty sequence.")
    average = mean(values)
    if len(values) == 1:
        return average, average, average
    margin = 1.96 * stdev(values) / sqrt(len(values))
    return average, average - margin, average + margin


class ConditionResult(BaseModel):
    """TRACE assessment for one agent--task condition across repeated runs."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str
    task_id: str
    task_category: str
    run_count: int
    success_mean: float
    latency_mean_ms: float
    signature: BehaviourSignature
    processing_time_ms: float
    peak_memory_kb: float
    error_event_count: int
    tool_failure_count: int


class AgentResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str
    condition_count: int
    success_mean: float
    success_ci_low: float
    success_ci_high: float
    latency_mean_ms: float
    cognitive_mean: float
    operational_mean: float
    reliability_mean: float
    confidence_mean: float
    confidence_std: float
    trace_score_mean: float
    final_score_mean: float


class StudyResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    validation: ValidationReport
    conditions: List[ConditionResult]
    agents: List[AgentResult]
    reproducibility_record: Dict[str, object]


def validate_records(manifest: ExperimentManifest, records: Sequence[ExecutionRecord]) -> ValidationReport:
    expected = {(agent.agent_id, task.task_id) for agent in manifest.agents for task in manifest.tasks}
    observed: Dict[Tuple[str, str], List[ExecutionRecord]] = defaultdict(list)
    run_ids = [record.run_id for record in records]
    for record in records:
        observed[(record.agent_id, record.task_id)].append(record)
    missing = sorted(f"{agent}/{task}" for agent, task in expected - set(observed))
    unexpected = sorted(f"{agent}/{task}" for agent, task in set(observed) - expected)
    invalid_counts = {
        f"{agent}/{task}": len(runs)
        for (agent, task), runs in observed.items()
        if (agent, task) in expected and len(runs) != manifest.repeated_runs_per_condition
    }
    duplicate_ids = sorted(run_id for run_id, count in Counter(run_ids).items() if count > 1)
    return ValidationReport(
        expected_conditions=len(expected),
        observed_conditions=len(observed),
        expected_runs=len(expected) * manifest.repeated_runs_per_condition,
        observed_runs=len(records),
        missing_conditions=missing,
        unexpected_conditions=unexpected,
        duplicate_run_ids=duplicate_ids,
        invalid_run_counts=invalid_counts,
    )


class StudyAnalyzer:
    """Analyse validated real execution records without generating benchmark data."""

    def __init__(self, pipeline: TRACEPipeline | None = None) -> None:
        self.pipeline = pipeline or TRACEPipeline()

    def analyze(self, manifest: ExperimentManifest, records: Sequence[ExecutionRecord]) -> StudyResult:
        validation = validate_records(manifest, records)
        if not validation.is_complete:
            raise ValueError(
                "Experiment record is incomplete: "
                f"missing={validation.missing_conditions}, unexpected={validation.unexpected_conditions}, invalid_counts={validation.invalid_run_counts}, "
                f"duplicate_ids={validation.duplicate_run_ids}"
            )
        task_categories = {task.task_id: task.category for task in manifest.tasks}
        min_bounds = {name: value["min"] for name, value in manifest.normalization_bounds.items()}
        max_bounds = {name: value["max"] for name, value in manifest.normalization_bounds.items()}
        pipeline = TRACEPipeline(
            category_weights=CategoryWeights(**manifest.category_weights),
            global_weights=GlobalCategoryWeights(**manifest.global_weights),
            min_bounds=min_bounds,
            max_bounds=max_bounds,
        )
        grouped: Dict[Tuple[str, str], List[ExecutionRecord]] = defaultdict(list)
        for record in records:
            grouped[(record.agent_id, record.task_id)].append(record)

        conditions: List[ConditionResult] = []
        for (agent_id, task_id), runs in sorted(grouped.items()):
            tracemalloc.start()
            started = perf_counter()
            signature = pipeline.evaluate_agent_runs([run.trace for run in runs])
            processing_time_ms = (perf_counter() - started) * 1000
            _, peak_bytes = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            latencies = [
                run.agent_latency_ms if run.agent_latency_ms is not None else run.trace.observed_duration_ms
                for run in runs
            ]
            events = [event for run in runs for event in run.trace.events]
            conditions.append(ConditionResult(
                agent_id=agent_id,
                task_id=task_id,
                task_category=task_categories[task_id],
                run_count=len(runs),
                success_mean=mean(run.success_score for run in runs),
                latency_mean_ms=mean(latencies),
                signature=signature,
                processing_time_ms=processing_time_ms,
                peak_memory_kb=peak_bytes / 1024,
                error_event_count=sum(event.is_error for event in events),
                tool_failure_count=sum(event.is_error and event.category.value == "tool_use" for event in events),
            ))

        reproducibility_record = manifest.model_dump(mode="json")
        reproducibility_record.update({"observed_runs": len(records), "record_schema": "ExecutionRecord JSONL v1"})
        return StudyResult(
            validation=validation,
            conditions=conditions,
            agents=self._summarize_agents(conditions),
            reproducibility_record=reproducibility_record,
        )

    @staticmethod
    def _summarize_agents(conditions: Sequence[ConditionResult]) -> List[AgentResult]:
        grouped: Dict[str, List[ConditionResult]] = defaultdict(list)
        for condition in conditions:
            grouped[condition.agent_id].append(condition)
        summaries: List[AgentResult] = []
        for agent_id, values in sorted(grouped.items()):
            success, low, high = _mean_ci([item.success_mean for item in values])
            confidences = [item.signature.confidence for item in values]
            summaries.append(AgentResult(
                agent_id=agent_id,
                condition_count=len(values),
                success_mean=success,
                success_ci_low=low,
                success_ci_high=high,
                latency_mean_ms=mean(item.latency_mean_ms for item in values),
                cognitive_mean=mean(item.signature.cognitive for item in values),
                operational_mean=mean(item.signature.operational for item in values),
                reliability_mean=mean(item.signature.reliability for item in values),
                confidence_mean=mean(confidences),
                confidence_std=stdev(confidences) if len(confidences) > 1 else 0.0,
                trace_score_mean=mean(item.signature.compute_trace_score() for item in values),
                final_score_mean=mean(item.signature.compute_final_score() for item in values),
            ))
        return summaries
