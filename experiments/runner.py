"""
TRACE Experiment Runner.

Executes controlled multi-agent benchmark trials, measures computational overhead,
and collects data needed to generate Section 5 experimental tables and figures.
"""

import time
import tracemalloc
from typing import Dict, List, Any
import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from trace.assessment.signature import BehaviourSignature
from trace.domain.trace import BehaviourTrace
from trace.pipeline import TRACEPipeline


class ExperimentResult(BaseModel):
    """Encapsulates execution metrics and behavioural signatures for an agent."""

    model_config = ConfigDict(frozen=True)

    agent_id: str
    num_runs: int
    signature: BehaviourSignature
    task_success_rate: float
    avg_latency_sec: float
    processing_time_ms: float
    memory_peak_kb: float
    protocol_overhead_pct: float


class ExperimentRunner:
    """Orchestrates benchmark executions across heterogeneous agents."""

    def __init__(self, pipeline: TRACEPipeline | None = None):
        self.pipeline = pipeline or TRACEPipeline()

    def run_agent_experiment(
        self,
        agent_id: str,
        traces: List[BehaviourTrace],
        task_successes: List[bool],
        agent_latencies_sec: List[float],
    ) -> ExperimentResult:
        """
        Runs pipeline evaluation over N repeated traces, profiling runtime overhead.
        """
        if not traces:
            raise ValueError("Traces list cannot be empty.")

        # Measure baseline agent timing
        total_agent_time = sum(agent_latencies_sec)
        success_rate = (sum(task_successes) / len(task_successes)) * 100.0
        avg_latency = float(np.mean(agent_latencies_sec))

        # Profile TRACE overhead
        tracemalloc.start()
        start_time = time.perf_counter()

        signature = self.pipeline.evaluate_agent_runs(traces)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_kb = peak_bytes / 1024.0

        # Overhead = (TRACE time / (Agent time + TRACE time)) * 100
        total_time_sec = total_agent_time + (elapsed_ms / 1000.0)
        overhead_pct = ((elapsed_ms / 1000.0) / total_time_sec * 100.0) if total_time_sec > 0 else 0.0

        return ExperimentResult(
            agent_id=agent_id,
            num_runs=len(traces),
            signature=signature,
            task_success_rate=success_rate,
            avg_latency_sec=avg_latency,
            processing_time_ms=elapsed_ms,
            memory_peak_kb=peak_kb,
            protocol_overhead_pct=overhead_pct,
        )