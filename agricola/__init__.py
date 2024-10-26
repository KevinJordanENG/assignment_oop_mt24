"""
Entry point for the agricola game pkg.
"""

from __future__ import annotations
from .game import Game

# Export single item tuple of 'Game' API / facade class for pkg level direct access.
__all__ = ("Game",)
