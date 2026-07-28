"""
Unit tests for TRACE Synthetic Trace Generator.
"""

from trace.experiments.generator import SyntheticTraceGenerator


def test_synthetic_trace_generator_single():
    generator = SyntheticTraceGenerator(seed=123)
    trace = generator.generate_agent_trace(
        agent_id="OpenAI_GPT5_Agent",
        task_id="reasoning_task",
        run_index=0,
        error_probability=0.0,
    )

    assert len(trace) == 4
    assert trace.agent_id == "OpenAI_GPT5_Agent"
    assert trace.task_id == "reasoning_task"
    assert trace.error_rate == 0.0


def test_synthetic_benchmark_suite_generation():
    generator = SyntheticTraceGenerator(seed=456)
    data = generator.generate_benchmark_suite(runs_per_agent=3)

    assert len(data) == 5
    for agent_id, (traces, successes, latencies) in data.items():
        assert len(traces) == 3
        assert len(successes) == 3
        assert len(latencies) == 3
        assert all(lat > 0 for lat in latencies)