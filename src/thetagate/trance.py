"""Simple trance depth calculation."""

from typing import Dict


def score(sample: Dict[str, float]) -> float:
    """Return a trance depth score from an EEG sample."""
    theta = sample.get("theta", 0.0)
    delta = sample.get("delta", 0.0)
    alpha = sample.get("alpha", 0.0)
    beta = sample.get("beta", 0.0)
    # Higher theta+delta relative to alpha+beta indicates deeper trance
    denominator = alpha + beta
    if denominator == 0:
        return 0.0
    return (theta + delta) / denominator * 10.0
