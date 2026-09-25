"""
TRACE Experiment Execution, Benchmarking, and LaTeX Export Engine.
"""

from .exporter import LaTeXExporter
from .generator import SyntheticTraceGenerator
from .runner import ExperimentResult, ExperimentRunner
from .analysis import StudyAnalyzer, StudyResult
from .contracts import ExecutionRecord, ExperimentManifest
from .recorder import TraceRecorder

__all__ = [
    "ExperimentResult",
    "ExperimentRunner",
    "LaTeXExporter",
    "SyntheticTraceGenerator",
    "ExecutionRecord",
    "ExperimentManifest",
    "StudyAnalyzer",
    "StudyResult",
    "TraceRecorder",
]
