"""Command-line interface for ThetaGate."""

import argparse
from pathlib import Path
from . import eeg, trance, script_runner, speech


def _start_web(host: str, port: int) -> None:
    from . import web

    web.app.run(host=host, port=port)


def run(args: argparse.Namespace) -> None:
    if args.command == "monitor":
        print("Streaming simulated EEG data. Press Ctrl+C to stop.")
        try:
            for sample in eeg.stream(interval=args.interval):
                tscore = trance.score(sample)
                ratio = trance.alpha_theta_ratio(sample)
                crossover = trance.alpha_theta_crossover(sample)
                msg = (
                    f"Sample {sample} :: Trance score {tscore:.2f} :: "
                    f"theta/alpha {ratio:.2f}"
                )
                if crossover and not args.no_crossover_alert:
                    msg += " << alpha-theta crossover"
                print(msg)
        except KeyboardInterrupt:
            print("\nStopping stream.")
    elif args.command == "run-script":
        path = Path(args.file)
        lines = path.read_text().splitlines()
        print(f"Running script: {path}")
        settings = None
        if args.voice_id:
            settings = speech.SpeechSettings(
                voice_id=args.voice_id,
                stability=args.stability,
                similarity_boost=args.similarity_boost,
                style=args.style,
                use_speaker_boost=args.speaker_boost,
                api_key=args.api_key,
            )
        script_runner.run_script(lines, delay=args.delay, speech_settings=settings)
    elif args.command == "web":
        _start_web(args.host, args.port)
    else:
        print("Unknown command")


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ThetaGate CLI")
    sub = parser.add_subparsers(dest="command")

    mon = sub.add_parser("monitor", help="Stream simulated EEG")
    mon.add_argument("--interval", type=float, default=1.0, help="Sample interval")
    mon.add_argument(
        "--no-crossover-alert",
        action="store_true",
        help="Suppress alpha-theta crossover messages",
    )

    sc = sub.add_parser("run-script", help="Run hypnosis script")
    sc.add_argument("file", help="Path to script file")
    sc.add_argument("--delay", type=float, default=5.0, help="Delay between lines")
    sc.add_argument("--voice-id", help="ElevenLabs voice ID to use for speech")
    sc.add_argument("--stability", type=float, default=0.75, help="Voice stability")
    sc.add_argument(
        "--similarity-boost",
        type=float,
        default=0.75,
        help="Voice similarity boost",
    )
    sc.add_argument("--style", type=float, default=None, help="Voice style")
    sc.add_argument(
        "--no-speaker-boost",
        dest="speaker_boost",
        action="store_false",
        help="Disable speaker boost",
    )
    sc.add_argument(
        "--api-key",
        help="ElevenLabs API key (defaults to ELEVENLABS_API_KEY env variable)",
    )
    web_cmd = sub.add_parser("web", help="Start web interface")
    web_cmd.add_argument("--host", default="127.0.0.1", help="Host to bind")
    web_cmd.add_argument("--port", type=int, default=5000, help="Port to bind")


    return parser.parse_args(argv)


if __name__ == "__main__":
    run(parse_args())
