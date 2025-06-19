"""Command-line interface for ThetaGate."""

import argparse
from pathlib import Path
from . import eeg, trance, script_runner


def run(args: argparse.Namespace) -> None:
    if args.command == "monitor":
        print("Streaming simulated EEG data. Press Ctrl+C to stop.")
        try:
            for sample in eeg.stream(interval=args.interval):
                tscore = trance.score(sample)
                print(f"Sample {sample} :: Trance score {tscore:.2f}")
        except KeyboardInterrupt:
            print("\nStopping stream.")
    elif args.command == "run-script":
        path = Path(args.file)
        lines = path.read_text().splitlines()
        print(f"Running script: {path}")
        script_runner.run_script(lines, delay=args.delay)
    else:
        print("Unknown command")


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ThetaGate CLI")
    sub = parser.add_subparsers(dest="command")

    mon = sub.add_parser("monitor", help="Stream simulated EEG")
    mon.add_argument("--interval", type=float, default=1.0, help="Sample interval")

    sc = sub.add_parser("run-script", help="Run hypnosis script")
    sc.add_argument("file", help="Path to script file")
    sc.add_argument("--delay", type=float, default=5.0, help="Delay between lines")

    return parser.parse_args(argv)


if __name__ == "__main__":
    run(parse_args())
