"""
TRACE Synthetic Trace Dataset Generator.

Generates realistic BehaviourTrace benchmarks simulating agent interactions across
various tasks and ecosystems (OpenAI, Anthropic, Google, Qwen, DeepSeek).
"""

from datetime import datetime, timedelta, timezone
import random
from typing import Dict, List, Tuple

from trace.domain.primitives import EventCategory, ObservableEvidence
from trace.domain.trace import BehaviourTrace


class SyntheticTraceGenerator:
    """Generates synthetic execution traces for benchmark agent evaluations."""

    AGENTS = [
        "OpenAI_GPT5_Agent",
        "Anthropic_ClaudeOpus4_Agent",
        "Google_Gemini25Pro_Agent",
        "Qwen3_Agent",
        "DeepSeek_R1_Agent",
    ]

    TASK_CATEGORIES = [
        "reasoning_task",
        "planning_task",
        "tool_assisted_task",
        "memory_task",
        "adaptive_task",
        "failure_recovery_task",
        "end_to_end_task",
    ]

    def __init__(self, seed: int = 42):
        random.seed(seed)

    def generate_agent_trace(
        self,
        agent_id: str,
        task_id: str,
        run_index: int,
        error_probability: float = 0.1,
    ) -> BehaviourTrace:
        """Generate a single realistic BehaviourTrace for a given agent and task."""
        t0 = datetime.now(timezone.utc) - timedelta(hours=run_index)
        events: List[ObservableEvidence] = []
        current_time = t0

        # Step 1: Planning Event
        p_latency = random.uniform(80.0, 200.0)
        events.append(
            ObservableEvidence(
                event_id=f"{agent_id}_{task_id}_e1",
                timestamp=current_time,
                category=EventCategory.PLANNING,
                action_name="decompose_objective",
                payload={"plan_steps": ["search", "compute", "format"]},
                latency_ms=p_latency,
            )
        )
        current_time += timedelta(milliseconds=p_latency)

        # Step 2: Reasoning Event
        r_latency = random.uniform(100.0, 300.0)
        events.append(
            ObservableEvidence(
                event_id=f"{agent_id}_{task_id}_e2",
                timestamp=current_time,
                category=EventCategory.REASONING,
                action_name="analyze_context",
                payload={"thought_process": "Evaluating query context and required tools."},
                latency_ms=r_latency,
            )
        )
        current_time += timedelta(milliseconds=r_latency)

        # Step 3: Tool Use Event (with controlled error chance)
        t_latency = random.uniform(150.0, 450.0)
        is_error = random.random() < error_probability
        events.append(
            ObservableEvidence(
                event_id=f"{agent_id}_{task_id}_e3",
                timestamp=current_time,
                category=EventCategory.TOOL_USE,
                action_name="execute_database_query",
                payload={"query": "SELECT * FROM benchmark_db;"},
                latency_ms=t_latency,
                is_error=is_error,
            )
        )
        current_time += timedelta(milliseconds=t_latency)

        # Step 4: Recovery or Verification Step
        v_latency = random.uniform(90.0, 250.0)
        events.append(
            ObservableEvidence(
                event_id=f"{agent_id}_{task_id}_e4",
                timestamp=current_time,
                category=EventCategory.REASONING,
                action_name="verify_result" if not is_error else "recover_from_error",
                payload={"outcome": "Success" if not is_error else "Handled exception"},
                latency_ms=v_latency,
                is_error=False,  # Recovered successfully
            )
        )

        return BehaviourTrace(
            trace_id=f"tr_{agent_id}_{task_id}_{run_index}",
            task_id=task_id,
            agent_id=agent_id,
            events=events,
        )

    def generate_benchmark_suite(
        self, runs_per_agent: int = 5
    ) -> Dict[str, Tuple[List[BehaviourTrace], List[bool], List[float]]]:
        """
        Generate complete benchmark traces, task successes, and latencies for all 5 agents.
        """
        benchmark_data = {}

        # Define profile characteristics for different agents
        agent_error_rates = {
            "OpenAI_GPT5_Agent": 0.05,
            "Anthropic_ClaudeOpus4_Agent": 0.04,
            "Google_Gemini25Pro_Agent": 0.08,
            "Qwen3_Agent": 0.12,
            "DeepSeek_R1_Agent": 0.06,
        }

        for agent_id in self.AGENTS:
            traces = []
            successes = []
            latencies = []
            err_rate = agent_error_rates.get(agent_id, 0.1)

            for run in range(runs_per_agent):
                task_id = random.choice(self.TASK_CATEGORIES)
                trace = self.generate_agent_trace(
                    agent_id=agent_id,
                    task_id=task_id,
                    run_index=run,
                    error_probability=err_rate,
                )
                traces.append(trace)
                successes.append(not trace.events[2].is_error)
                latencies.append(trace.total_duration_ms / 1000.0)

            benchmark_data[agent_id] = (traces, successes, latencies)

        return benchmark_data