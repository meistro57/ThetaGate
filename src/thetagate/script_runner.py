"""Play back a hypnosis script."""

import time
from typing import Iterable


def run_script(lines: Iterable[str], delay: float = 5.0) -> None:
    """Print each line with a delay."""
    for line in lines:
        print(line.strip())
        time.sleep(delay)
