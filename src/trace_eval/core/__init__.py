"""
TRACE Core
==========

The ``trace.core`` package provides the foundational building blocks shared
across the TRACE framework.

This package is intentionally lightweight and dependency-free. It contains
shared types, constants, protocols, version information, and metadata that
are used throughout the framework.

Modules in higher architectural layers may depend on ``trace.core``, but
``trace.core`` must never depend on those higher layers.
"""

from __future__ import annotations

from .metadata import (
    __author__,
    __copyright__,
    __license__,
    __title__,
    __version__,
)

__all__: list[str] = [
    "__title__",
    "__version__",
    "__author__",
    "__license__",
    "__copyright__",
]
