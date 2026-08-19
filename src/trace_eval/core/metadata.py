"""
TRACE framework metadata.

This module provides the canonical package metadata used throughout the
TRACE framework. Package identity should be defined here only, ensuring a
single source of truth for metadata consumed by runtime code, packaging,
and documentation.

The project follows Semantic Versioning (SemVer):

    MAJOR.MINOR.PATCH

Version increments:
    • MAJOR: Breaking protocol or API changes.
    • MINOR: New backwards-compatible functionality.
    • PATCH: Backwards-compatible bug fixes.
"""

from __future__ import annotations

from typing import Final

__title__: Final[str] = "TRACE"

__version__: Final[str] = "0.1.0"

__author__: Final[str] = "TRACE Research Team"

__license__: Final[str] = "MIT"

__copyright__: Final[str] = (
    "Copyright (c) 2026 TRACE Research Team"
)

__repository__: Final[str] = (
    "https://github.com/genzybas/trace"
)

__python_requires__: Final[str] = ">=3.12"

VERSION: Final[tuple[int, int, int]] = (
    0,
    1,
    0,
)

__all__: list[str] = [
    "__title__",
    "__version__",
    "__author__",
    "__license__",
    "__copyright__",
    "__repository__",
    "__python_requires__",
    "VERSION",
]