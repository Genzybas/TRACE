from trace_eval.experiments.generator import SyntheticTraceGenerator
from trace_eval.experiments.runner import ExperimentRunner
from trace_eval.experiments.exporter import LaTeXExporter
from trace_eval.experiments.exporters_multi import MultiFormatExporter
from trace_eval.experiments.visualizer import TRACEVisualizer

def main():
    print("1. Generating synthetic benchmark traces for 5 agent ecosystems...")
    # Generate benchmark dataset matching manuscript Section 4.2
    generator = SyntheticTraceGenerator(seed=42)
    benchmark_data = generator.generate_benchmark_suite(runs_per_agent=10)

    print("2. Running TRACE evaluation pipeline across all agents...")
    runner = ExperimentRunner()
    results = []
    for agent_id, (traces, successes, latencies) in benchmark_data.items():
        res = runner.run_agent_experiment(agent_id, traces, successes, latencies)
        results.append(res)

    print("\n" + "=" * 60)
    print("SECTION 5 LATEX TABLES EXPORT")
    print("=" * 60)

    # Table 3: Behavioural Characterization
    print("\n--- TABLE 3: BEHAVIOURAL CHARACTERIZATION ---")
    table_3_latex = LaTeXExporter.export_table_3_characterization(results)
    print(table_3_latex)

    # Table 5: Conventional Metrics vs TRACE Characterization
    print("\n--- TABLE 5: METRICS VS TRACE ---")
    table_5_latex = LaTeXExporter.export_table_5_metrics_vs_trace(results)
    print(table_5_latex)

    # Table 7: Computational Characteristics
    print("\n--- TABLE 7: COMPUTATIONAL OVERHEAD ---")
    table_7_latex = LaTeXExporter.export_table_7_computational(results)
    print(table_7_latex)

    print("\n" + "=" * 60)
    print("SAVING LATEX TABLES TO FILES")
    print("=" * 60)
    with open("section5_tables.tex", "w", encoding="utf-8") as f:
        f.write("% Table 3\n" + table_3_latex + "\n\n")
        f.write("% Table 5\n" + table_5_latex + "\n\n")
        f.write("% Table 7\n" + table_7_latex + "\n")
    print("LaTeX code saved to 'section5_tables.tex'.")

    print("\n" + "=" * 60)
    print("GENERATING & SAVING FIGURES")
    print("=" * 60)
    # Generate and save Figure 6 (Radar Chart) and Score vs Success Bar Plot
    TRACEVisualizer.plot_behavioural_radar(results, output_path="behavioural_signatures_radar.png")
    print("Saved 'behavioural_signatures_radar.png'")

    TRACEVisualizer.plot_score_vs_success_bar(results, output_path="score_vs_success_bar.png")
    print("Saved 'score_vs_success_bar.png'")

    # Optional: Save Markdown and CSV summaries
    with open("benchmark_results.md", "w", encoding="utf-8") as f:
        f.write(MultiFormatExporter.export_to_markdown(results))
    print("Saved Markdown summary to 'benchmark_results.md'")

    with open("benchmark_results.csv", "w", encoding="utf-8") as f:
        f.write(MultiFormatExporter.export_to_csv(results))
    print("Saved CSV summary to 'benchmark_results.csv'")

if __name__ == "__main__":
    main()