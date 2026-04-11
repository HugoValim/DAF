"""Experiment configuration utilities — re-exports predefined samples from mode_parser."""

from dataclasses import dataclass

from daf.core.mode_parser import PREDEFINED_MATERIALS as samples


# Re-export for backward compatibility
__all__ = ["samples"]


@dataclass
class Hi:
    """Placeholder dataclass — not used in production."""
    one: str = "oioi"
    two: str = "oi"
