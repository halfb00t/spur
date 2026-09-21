"""spur — parametric involute spur gear generator."""

import os

__version__ = "0.1.0"


def int_env(name: str, default: int) -> int:
    """A positive integer setting from the environment, falling back on nonsense."""
    try:
        return max(1, int(os.environ.get(name) or default))
    except ValueError:
        return default
