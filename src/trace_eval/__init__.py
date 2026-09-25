"""
TRACE Framework
===============

TRACE (Behaviour-Centric Evaluation Protocol) is a research framework for
evaluating AI-generated text through behavioural analysis rather than
surface-level linguistic characteristics.

The framework implements the complete TRACE behavioural pipeline:

    ObservableEvidence
            ↓
      BehaviourTrace
            ↓
      BehaviourVector
            ↓
     BehaviourProfile
            ↓
   BehaviourConfidence
            ↓
    BehaviourSignature
            ↓
        TRACE Score

This package exposes only the stable public API. Internal modules should
be imported from their respective packages and are not considered part of
the public interface unless explicitly re-exported here.
"""

from __future__ import annotations

from trace_eval.core.metadata import (
    __author__,
    __license__,
    __title__,
    __version__,
)
from trace_eval.pipeline import TRACEPipeline

__all__ = [
    "__title__",
    "__version__",
    "__author__",
    "__license__",
    "TRACEPipeline",
]