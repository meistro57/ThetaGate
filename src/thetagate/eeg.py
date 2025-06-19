"""Simulated EEG data generator."""

import random
from typing import Iterator, Dict
import time

BANDS = ["delta", "theta", "alpha", "beta"]


def sample() -> Dict[str, float]:
    """Return a single EEG band power sample."""
    return {band: random.uniform(0.0, 100.0) for band in BANDS}


def stream(interval: float = 1.0) -> Iterator[Dict[str, float]]:
    """Generate EEG samples forever at the given interval (in seconds)."""
    while True:
        yield sample()
        time.sleep(interval)
