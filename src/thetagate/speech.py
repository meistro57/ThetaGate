"""Utilities for ElevenLabs speech synthesis."""

from dataclasses import dataclass
from typing import Optional, Iterable
import os

from elevenlabs import play
from elevenlabs.client import ElevenLabs
from elevenlabs.types import VoiceSettings


@dataclass
class SpeechSettings:
    """Configuration for speech synthesis."""

    voice_id: str
    stability: float = 0.75
    similarity_boost: float = 0.75
    style: Optional[float] = None
    use_speaker_boost: bool = True
    api_key: Optional[str] = None


def synthesize(text: str, settings: SpeechSettings) -> bytes:
    """Generate speech audio from text using ElevenLabs."""
    client = ElevenLabs(api_key=settings.api_key or os.getenv("ELEVENLABS_API_KEY"))
    vs = VoiceSettings(
        stability=settings.stability,
        similarity_boost=settings.similarity_boost,
        style=settings.style,
        use_speaker_boost=settings.use_speaker_boost,
    )
    audio = client.text_to_speech.convert(
        voice_id=settings.voice_id,
        text=text,
        voice_settings=vs,
        output_format="mp3_44100_128",
    )
    if isinstance(audio, (bytes, bytearray)):
        return bytes(audio)
    return b"".join(audio)


def speak(text: str, settings: SpeechSettings, play_audio: bool = True) -> bytes:
    """Generate and optionally play speech audio."""
    audio = synthesize(text, settings)
    if play_audio:
        play(audio)
    return audio
