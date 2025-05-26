"""High-level Python wrapper for libisyntax.

This package provides the :class:`Isyntax` class which mimics the OpenSlide
interface for reading Philips iSyntax files.
"""

from .isyntax import Isyntax

__all__ = ["Isyntax"]
