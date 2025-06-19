"""Play back a hypnosis script with optional speech synthesis."""

import time
from typing import Iterable, Optional

from . import speech


def run_script(
    lines: Iterable[str],
    delay: float = 5.0,
    speech_settings: Optional[speech.SpeechSettings] = None,
) -> None:
    """Print each line with a delay and optionally speak it."""
    for line in lines:
        text = line.strip()
        print(text)
        if speech_settings:
            speech.speak(text, speech_settings)
        time.sleep(delay)
