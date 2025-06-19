from flask import Flask, render_template_string, Response, request
from pathlib import Path
import json
import threading

from . import eeg, script_runner

app = Flask(__name__)

HTML = """
<!doctype html>
<title>ThetaGate</title>
<h1>ThetaGate Web UI</h1>
<h2>EEG Stream</h2>
<pre id="stream">Connecting...</pre>

<script>
var source = new EventSource('/samples');
source.onmessage = function(event) {
    document.getElementById('stream').textContent = event.data;
};
</script>

<h2>Run Script</h2>
<form action="/run-script" method="post">
    <label>Path: <input type="text" name="path" value="scripts/sample.txt" size="40"></label><br>
    <label>Delay: <input type="number" step="0.1" name="delay" value="5.0"></label><br>
    <button type="submit">Run</button>
</form>
"""


@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/samples')
def samples():
    def generate():
        for sample in eeg.stream(1.0):
            yield f"data: {json.dumps(sample)}\n\n"
    return Response(generate(), mimetype='text/event-stream')


def _run_script(path: str, delay: float) -> None:
    lines = Path(path).read_text().splitlines()
    script_runner.run_script(lines, delay=delay)


@app.post('/run-script')
def run_script():
    path = request.form.get('path', 'scripts/sample.txt')
    delay = float(request.form.get('delay', 5.0))
    thread = threading.Thread(target=_run_script, args=(path, delay), daemon=True)
    thread.start()
    return 'Running script...'


if __name__ == '__main__':
    app.run()
