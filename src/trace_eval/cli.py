"""Command line entry points for single-trace and reproducible study analysis."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from trace_eval.assessment.confidence import BehaviourConfidenceEstimator
from trace_eval.domain.trace import BehaviourTrace
from trace_eval.experiments.analysis import StudyAnalyzer
from trace_eval.experiments.io import load_execution_records, load_manifest, write_csv, write_json
from trace_eval.experiments.reporting import StudyLaTeXExporter
from trace_eval.pipeline import TRACEPipeline


def load_traces_from_json(file_path: str) -> List[BehaviourTrace]:
    """Load and validate BehaviourTrace instances from a JSON file."""
    with open(file_path, encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, dict):
        data = [data]
    return [BehaviourTrace.model_validate(item) for item in data]


def _agent_rows(study: object) -> List[dict]:
    return [agent.model_dump() for agent in study.agents]


def _condition_rows(study: object) -> List[dict]:
    rows = []
    for condition in study.conditions:
        row = condition.model_dump()
        signature = row.pop("signature")
        row.update({
            "cognitive": signature["cognitive"],
            "operational": signature["operational"],
            "reliability": signature["reliability"],
            "confidence": signature["confidence"],
            "trace_score": condition.signature.compute_trace_score(),
            "final_score": condition.signature.compute_final_score(),
        })
        rows.append(row)
    return rows


def analyze_study(manifest_path: str, runs_path: str, output_directory: str) -> None:
    manifest = load_manifest(manifest_path)
    records = load_execution_records(runs_path)
    study = StudyAnalyzer().analyze(manifest, records)
    output = Path(output_directory)
    write_json(output / "study_result.json", study)
    write_json(output / "reproducibility_record.json", study.reproducibility_record)
    write_csv(output / "agent_summary.csv", _agent_rows(study))
    write_csv(output / "condition_results.csv", _condition_rows(study))
    (output / "tables.tex").write_text(StudyLaTeXExporter.export(study), encoding="utf-8")
    print(f"TRACE study analysis complete. Results written to {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="TRACE: multi-dimensional evaluation for LLM agents")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Analyse a manifest and real JSONL execution records.")
    analyze.add_argument("--manifest", required=True, help="Pre-registered experiment manifest JSON file.")
    analyze.add_argument("--runs", required=True, help="JSONL file of ExecutionRecord objects from real runs.")
    analyze.add_argument("--output", required=True, help="Directory for validated results and reproducibility artifacts.")

    single = subparsers.add_parser("single", help="Evaluate an existing JSON trace collection.")
    single.add_argument("--input", required=True, help="JSON file containing BehaviourTrace objects.")
    single.add_argument("--output", help="Optional output JSON file.")
    single.add_argument("--lambda-sensitivity", type=float, default=1.0)

    args = parser.parse_args()
    try:
        if args.command == "analyze":
            analyze_study(args.manifest, args.runs, args.output)
            return
        traces = load_traces_from_json(args.input)
        pipeline = TRACEPipeline(
            confidence_estimator=BehaviourConfidenceEstimator(lambda_sensitivity=args.lambda_sensitivity)
        )
        result = pipeline.evaluate_agent_runs(traces).to_dict()
        if args.output:
            write_json(args.output, result)
            print(f"TRACE evaluation complete. Result saved to {args.output}")
        else:
            print(json.dumps(result, indent=2))
    except Exception as error:
        print(f"Error executing TRACE evaluation: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
