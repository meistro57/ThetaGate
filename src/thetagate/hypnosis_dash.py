"""Dash UI for guided hypnosis sessions with EEG feedback."""

from __future__ import annotations

import json
import threading
import time
from datetime import datetime
from pathlib import Path
from queue import Queue, Empty

from dash import Dash, dcc, html, Output, Input, State, no_update
import plotly.graph_objs as go

from . import eeg


LOG_DIR = Path("logs")
AUDIO_FILE = Path("scripts/sample.mp3")


class HypnosisSession:
    """Manage a hypnosis session with EEG streaming and logging."""

    def __init__(self, audio_file: Path = AUDIO_FILE, log_dir: Path = LOG_DIR) -> None:
        self.audio_file = audio_file
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.running = False
        self.data: list[dict[str, float]] = []
        self._queue: Queue[dict[str, float]] = Queue()
        self._stop_event = threading.Event()
        self._start_time = 0.0
        self.replay_data: list[dict[str, float]] | None = None

    # --------------------------------------------------------------
    def start(self) -> None:
        """Begin streaming EEG and play the audio."""
        if self.running:
            return
        self.running = True
        self.data.clear()
        self.replay_data = None
        self._queue = Queue()
        self._stop_event.clear()
        self._start_time = time.time()
        threading.Thread(target=self._stream_eeg, daemon=True).start()
        threading.Thread(target=self._play_audio, daemon=True).start()

    def stop(self) -> None:
        """Stop the session and save the log."""
        if not self.running:
            return
        self._stop_event.set()
        self.running = False
        self._save_log()

    # --------------------------------------------------------------
    def _play_audio(self) -> None:
        """Play the guidance audio if available."""
        try:
            if self.audio_file.exists():
                from playsound import playsound

                playsound(str(self.audio_file))
            else:
                print(f"Audio file {self.audio_file} not found. Skipping playback.")
        except Exception as exc:
            print(f"Audio playback failed: {exc}")
        finally:
            self.stop()

    def _stream_eeg(self) -> None:
        """Continuously read EEG samples until stopped."""
        for sample in eeg.stream(1.0):
            if self._stop_event.is_set():
                break
            timestamp = time.time() - self._start_time
            record = {"time": timestamp, **sample}
            self.data.append(record)
            self._queue.put(record)

    # --------------------------------------------------------------
    def get_new_samples(self) -> list[dict[str, float]]:
        """Return new samples collected since last call."""
        items = []
        while True:
            try:
                items.append(self._queue.get_nowait())
            except Empty:
                break
        return items

    def _save_log(self) -> None:
        if not self.data:
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = self.log_dir / f"session_{ts}.json"
        with open(path, "w") as f:
            json.dump(self.data, f, indent=2)
        print(f"Saved session log to {path}")


session = HypnosisSession()


# ---------------------------------------------------------------------------

def _load_log(path: Path) -> list[dict[str, float]]:
    with open(path) as f:
        return json.load(f)


def list_logs() -> list[Path]:
    return sorted(LOG_DIR.glob("session_*.json"))


def create_app() -> Dash:
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.H2("Guided Hypnosis Session"),
            html.Button("Start Session", id="start-btn"),
            dcc.Graph(id="eeg-graph"),
            dcc.Interval(id="tick", interval=1000, n_intervals=0),
            html.Div(id="status"),
            html.H3("Replay Session"),
            dcc.Dropdown(
                id="log-select",
                options=[{"label": p.name, "value": p.name} for p in list_logs()],
                placeholder="Select a log file",
            ),
            html.Button("Replay", id="replay-btn"),
        ]
    )

    traces = {band: {"x": [], "y": []} for band in eeg.BANDS}

    # ------------------------------------------------------
    @app.callback(Output("status", "children"), Input("start-btn", "n_clicks"), prevent_initial_call=True)
    def start(n_clicks: int) -> str:
        session.start()
        # clear traces
        for t in traces.values():
            t["x"].clear()
            t["y"].clear()
        return "Session started"

    # ------------------------------------------------------
    @app.callback(
        Output("eeg-graph", "figure"),
        Input("tick", "n_intervals"),
    )
    def update_graph(n: int):
        """Update live graph with new samples or replay data."""
        if session.replay_data is not None:
            fig = go.Figure()
            for band in eeg.BANDS:
                x = [d["time"] for d in session.replay_data]
                y = [d.get(band, 0.0) for d in session.replay_data]
                fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=band))
            fig.update_layout(xaxis_title="Time (s)", yaxis_title="Power")
            return fig

        new_samples = session.get_new_samples()
        for sample in new_samples:
            for band in eeg.BANDS:
                traces[band]["x"].append(sample["time"])
                traces[band]["y"].append(sample[band])

        fig = go.Figure()
        for band in eeg.BANDS:
            fig.add_trace(
                go.Scatter(
                    x=traces[band]["x"],
                    y=traces[band]["y"],
                    mode="lines",
                    name=band,
                )
            )
        fig.update_layout(xaxis_title="Time (s)", yaxis_title="Power")
        return fig

    # ------------------------------------------------------
    @app.callback(Output("log-select", "options"), Input("status", "children"))
    def refresh_logs(_status: str):
        return [{"label": p.name, "value": p.name} for p in list_logs()]

    # ------------------------------------------------------
    @app.callback(Output("status", "children", allow_duplicate=True), Input("replay-btn", "n_clicks"), State("log-select", "value"), prevent_initial_call=True)
    def replay(n_clicks: int, filename: str):
        if not filename:
            return no_update
        path = LOG_DIR / filename
        session.replay_data = _load_log(path)
        return f"Loaded {filename}"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
