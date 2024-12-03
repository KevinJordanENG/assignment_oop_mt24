"""
Entry point for the agricola game pkg.
"""

from __future__ import annotations
from .game import Game
from .state_server import StateError

# Export 'Game' API / facade pattern class for pkg level direct access.
# Also exports 'StateError' for better UX when out of turn illegal actions are attempted.
__all__ = ("Game", "StateError")
