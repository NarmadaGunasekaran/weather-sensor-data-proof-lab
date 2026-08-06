"""Local upload-and-compare web app for lossless weather-data compression."""

from __future__ import annotations

import hashlib
from pathlib import Path

from flask import Flask, render_template_string, request

from weather_compression.benchmark import benchmark
from weather_compression.sample import one_day_weather_payload

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_SUFFIXES = {".json", ".csv", ".txt"}

PAGE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Weather Data Compression Lab</title>
    <style>
      :root { --ink:#102940; --muted:#60778b; --line:#dce6ee; --paper:#fff; --surface:#f3f7fa; --blue:#2374df; --green:#08784b; --green-soft:#e8f8ef; --amber:#9c5b06; --amber-soft:#fff3df; --red:#ad2e38; --red-soft:#fdebed; }
      * { box-sizing:border-box; } body { margin:0; background:var(--surface); color:var(--ink); font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; } main { width:min(1050px,calc(100% - 32px)); margin:0 auto; padding:42px 0 68px; } .eyebrow { color:var(--blue); font-weight:800; font-size:.78rem; letter-spacing:.1em; text-transform:uppercase; } h1 { margin:7px 0; font-size:clamp(2rem,5vw,3.4rem); letter-spacing:-.055em; } h2 { margin:0 0 7px; letter-spacing:-.02em; } .intro { max-width:760px; color:var(--muted); line-height:1.55; } .card { margin-top:20px; padding:22px; border:1px solid var(--line); border-radius:16px; background:var(--paper); box-shadow:0 7px 22px rgba(36,73,103,.06); } form { display:flex; flex-wrap:wrap; align-items:end; gap:13px; } label { display:block; margin-bottom:6px; color:var(--muted); font-weight:800; font-size:.76rem; letter-spacing:.07em; text-transform:uppercase; } input[type=file] { max-width:330px; padding:8px; border:1px solid var(--line); border-radius:8px; } button { padding:11px 14px; border:1px solid var(--blue); border-radius:8px; color:#fff; background:var(--blue); cursor:pointer; font:inherit; font-weight:750; } button.secondary { color:#254d6d; border-color:#b7c9d8; background:#fff; } .hint { margin:14px 0 0; color:var(--muted); font-size:.85rem; line-height:1.5; } .error { border-color:#edb8be; color:var(--red); background:var(--red-soft); } .metrics { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; } .metric { padding:15px; border:1px solid var(--line); border-radius:11px; } .metric span { color:var(--muted); font-size:.76rem; } .metric strong { display:block; margin-top:7px; font-size:1.42rem; letter-spacing:-.04em; } .pass { color:var(--green); background:var(--green-soft); } table { width:100%; border-collapse:collapse; margin-top:14px; font-size:.9rem; } th,td { padding:11px 8px; border-bottom:1px solid var(--line); text-align:left; } th { color:var(--muted); text-transform:uppercase; font-size:.71rem; letter-spacing:.06em; } .winner { color:var(--green); font-weight:800; } code { overflow-wrap:anywhere; } .note { margin-top:16px; padding:13px; border-radius:10px; color:#725007; background:var(--amber-soft); font-size:.88rem; line-height:1.5; } @media (max-width:700px) { .metrics { grid-template-columns:repeat(2,1fr); } } @media (max-width:460px) { .metrics { grid-template-columns:1fr; } }
    </style>
  </head>
  <body>
    <main>
      <div class="eyebrow">Local Python web app</div>
      <h1>Weather Data Compression Lab</h1>
      <p class="intro">Upload one weather API response or weather-station export. The app compares a trained, sensor-aware lossless codec with standard compression methods and verifies that every method restores the exact original bytes.</p>
      <section class="card">
        <h2>Run a comparison</h2>
        <form method="post" enctype="multipart/form-data">
          <div><label for="weatherFile">Weather data file</label><input id="weatherFile" name="weather_file" type="file" accept=".json,.csv,.txt"></div>
          <button type="submit" name="action" value="upload">Upload and compare</button>
          <button class="secondary" type="submit" name="action" value="sample">Run included weather sample</button>
        </form>
        <p class="hint">Accepted: JSON, CSV, or TXT up to 10 MB. Files are processed in memory and are not saved by this app.</p>
      </section>
      {% if error %}<section class="card error"><strong>Upload not processed:</strong> {{ error }}</section>{% endif %}
      {% if report %}
        <section class="card">
          <h2>Lossless result: {{ report.source_name }}</h2>
          <div class="metrics">
            <div class="metric"><span>Original size</span><strong>{{ report.original_bytes }} B</strong></div>
            <div class="metric"><span>Best method</span><strong>{{ report.winner.name }}</strong></div>
            <div class="metric"><span>Best saving</span><strong>{{ '%.1f'|format(report.winner.saved * 100) }}%</strong></div>
            <div class="metric pass"><span>Lossless verification</span><strong>Passed</strong></div>
          </div>
          <p class="hint">Raw SHA-256: <code>{{ report.source_hash }}</code></p>
          <table><thead><tr><th>Method</th><th>Compressed bytes</th><th>Data saved</th><th>Compress</th><th>Decompress</th><th>Exact bytes restored</th></tr></thead><tbody>
            {% for row in report.rows %}<tr{% if loop.first %} class="winner"{% endif %}><td>{{ row.name }}</td><td>{{ row.bytes }}</td><td>{{ '%.1f'|format(row.saved * 100) }}%</td><td>{{ '%.2f'|format(row.compress_ms) }} ms</td><td>{{ '%.2f'|format(row.decompress_ms) }} ms</td><td>Yes</td></tr>{% endfor %}
          </tbody></table>
          <p class="note"><strong>How to explain this:</strong> the trained weather agent is trained once on included representative sample payloads, then used as a fixed reversible codec. It is a transparent prototype—not a claim about any proprietary AI system. Test representative production data before making savings or performance claims.</p>
        </section>
      {% endif %}
    </main>
  </body>
</html>
"""


def create_app() -> Flask:
    """Create the local web application without persisting uploaded data."""
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES

    @app.route("/", methods=["GET", "POST"])
    def index() -> str:
        error: str | None = None
        report: dict[str, object] | None = None
        if request.method == "POST":
            try:
                data, source_name = _get_payload()
                rows = benchmark(data)
                report = {
                    "source_name": source_name,
                    "original_bytes": f"{len(data):,}",
                    "source_hash": hashlib.sha256(data).hexdigest(),
                    "winner": rows[0],
                    "rows": rows,
                }
            except ValueError as exc:
                error = str(exc)
        return render_template_string(PAGE, error=error, report=report)

    @app.errorhandler(413)
    def upload_too_large(_: object) -> tuple[str, int]:
        return render_template_string(PAGE, error="The file is larger than the 10 MB limit.", report=None), 413

    return app


def _get_payload() -> tuple[bytes, str]:
    if request.form.get("action") == "sample":
        return one_day_weather_payload(), "included one-day weather API sample"

    uploaded = request.files.get("weather_file")
    if uploaded is None or not uploaded.filename:
        raise ValueError("Choose a JSON, CSV, or TXT weather-data file, or run the included sample.")
    suffix = Path(uploaded.filename).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise ValueError("Only JSON, CSV, and TXT files are accepted.")
    data = uploaded.read()
    if not data:
        raise ValueError("The uploaded file is empty.")
    return data, uploaded.filename


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5051, debug=True)
