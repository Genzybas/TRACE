"""Input/output helpers for TRACE manifests and JSONL execution evidence."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List

from trace_eval.experiments.contracts import ExecutionRecord, ExperimentManifest


def load_manifest(path: str | Path) -> ExperimentManifest:
    with Path(path).open(encoding="utf-8") as handle:
        return ExperimentManifest.model_validate(json.load(handle))


def load_execution_records(path: str | Path) -> List[ExecutionRecord]:
    records: List[ExecutionRecord] = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(ExecutionRecord.model_validate_json(line))
            except Exception as error:
                raise ValueError(f"Invalid JSONL execution record at line {line_number}: {error}") from error
    if not records:
        raise ValueError("Execution-record JSONL file is empty.")
    return records


def write_json(path: str | Path, value: object) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    with output.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2)


def write_csv(path: str | Path, rows: List[dict]) -> None:
    """Write a rectangular collection of result rows as UTF-8 CSV."""
    if not rows:
        return
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
