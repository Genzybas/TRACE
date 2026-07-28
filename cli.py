"""
Command-Line Interface (CLI) for TRACE Evaluation Protocol.

Provides direct terminal operations for evaluating JSON BehaviourTrace files and
generating diagnostic BehaviourSignatures and TRACE Scores.
"""

import argparse
import json
import sys
from typing import List

from trace.assessment.signature import BehaviourSignature
from trace.domain.trace import BehaviourTrace
from trace.pipeline import TRACEPipeline


def load_traces_from_json(file_path: str) -> List[BehaviourTrace]:
    """Load and validate BehaviourTrace instances from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = [data]

    traces = [BehaviourTrace.model_validate(item) for item in data]
    return traces


def main() -> None:
    """CLI execution entrypoint."""
    parser = argparse.ArgumentParser(
        description="TRACE: Multi-Dimensional Evaluation Protocol for LLM Agents"
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to JSON file containing recorded BehaviourTrace(s).",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=False,
        help="Path to save output BehaviourSignature JSON.",
    )
    parser.add_argument(
        "--lambda-sensitivity",
        "-l",
        type=float,
        default=1.0,
        help="Sensitivity scaling parameter lambda for confidence decay (default: 1.0).",
    )

    args = parser.parse_args()

    try:
        traces = load_traces_from_json(args.input)
        pipeline = TRACEPipeline()
        pipeline.confidence_estimator.lambda_sensitivity = args.lambda_sensitivity

        signature: BehaviourSignature = pipeline.evaluate_agent_runs(traces)
        result = signature.to_dict()

        output_json = json.dumps(result, indent=2)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_json)
            print(f"TRACE Evaluation complete. Result saved to {args.output}")
        else:
            print(output_json)

    except Exception as e:
        print(f"Error executing TRACE evaluation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()