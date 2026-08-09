# Lossless Weather API Compression Benchmark

This project compares two ways to compress one day of weather API data:

1. **Trained weather agent** — a lightweight, AI-inspired codec that learns a fixed prediction profile from historical weather samples, predicts the next byte at runtime, and compresses exact residuals.
2. **Standard algorithms** — `zlib`, `gzip`, `bz2`, and `lzma` from Python's standard library.

Every codec is lossless: the benchmark decompresses each result and checks that its SHA-256 hash exactly matches the original input bytes.

## Recruiter-ready dashboard

Open `index.html` directly in any web browser to view the visual project summary. It is a standalone static page, so it can be published with GitHub Pages without a server.

## Recruiter formats

- Open `recruiter-one-page.html` for a printable one-page project summary.
- Open `weather-project-story.html` for a narrated, animated video-style project story.
- Open `Weather_Compression_Recruiter_Deck.pptx` for the editable five-slide recruiter presentation.

## Python upload web app

The `webapp/` folder contains a local Flask application. Upload one JSON, CSV, or TXT weather-data file (up to 10 MB), or run the included sample. It processes the file in memory, compares the trained weather agent with standard codecs, and shows only when every codec restores the exact original bytes.

```bash
cd weather-lossless-compression
python3 -m pip install -r webapp/requirements.txt
PYTHONPATH=src python3 webapp/app.py
```

Keep that Terminal window open, then open `http://127.0.0.1:5051` in a browser. Port `5051` avoids conflicts with other local applications that may already use port `5000`.

## Narrated explainer

Open `video-explainer.html` in a web browser and select **Play explanation**. It is a two-minute, captioned, beginner-friendly video-style walkthrough with a local WAV narration track.

## Compression Trust Monitor prototype

Open `trust-monitor.html` to demonstrate how a QA-focused deployment dashboard could monitor compression savings, losslessness, data drift, corruption checks, and staged rollouts for different customer sensor scenarios. It is a reusable concept and is not connected to any company system or based on private data.

## Edge Transmission Savings Simulator

Open `edge-savings-simulator.html` to turn a lossless compression percentage into editable 30-day network-traffic, transmission-cost, and radio-energy planning estimates. It addresses the customer-value side of compression; use measured device and tariff assumptions before making real-world claims.

## Weather Sensor Data Proof Lab

Open `pilot-lab.html` for an integrated weather-data demo. It models a **shadow PoC**: weather-station packets are mirrored for evaluation while the original production route remains unchanged. It generates synthetic temperature, humidity, and wind-speed packets, applies a small reversible edge codec, verifies byte-for-byte reconstruction, detects drift or corrupted packets, compares with browser GZIP, and downloads a privacy-conscious **Compression Passport** JSON report with the measured validation evidence. The Customer Value Planner turns the demo's measured saving into clearly labelled estimates for same-network capacity, higher sampling rate, and monthly data/cloud cost. The multi-sensor discovery panel also groups anonymous channels from 24 combined packets and suggests a label for each channel from its observed characteristics; suggestions require metadata or domain confirmation before specialised routing. It is a browser prototype, not a production agent or real customer-data integration.

Use `Weather_Proof_Lab_Explainer.pptx` for the step-by-step explanation of the interactive lab.

## Optional Claude API insights

The lossless encoder and decoder remain deterministic Python code. `weather_compression/claude_insights.py` is an optional Claude API helper that turns a completed benchmark or drift report into a plain-language summary and recommended human follow-up. It never decides how to encode or decode data.

```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key"
PYTHONPATH=src python3 -m weather_compression.claude_insights examples/vibration_drift_report.json
```

The trained-agent approach is deliberately transparent. It has a separate train-once phase and then uses a fixed profile at runtime. It demonstrates a general sensor-aware compression principle: adapt encoding to the structure of time-series data while preserving every original value.

Read `LEARNING_GUIDE.md` for a non-technical walkthrough and an interview-ready explanation.

## Run

Requires Python 3.11+ and no third-party packages.

```bash
cd weather-lossless-compression
python3 -m weather_compression.benchmark
```

Create a reusable agent artifact from representative historical payloads:

```bash
python3 -m weather_compression.train_agent --output weather-agent.json historical-day-1.json historical-day-2.json
```

With no input files, the training command uses the included seven-day demonstration dataset.

Benchmark your own one-day API response:

```bash
python3 -m weather_compression.benchmark /path/to/weather-day.json
```

The input is treated as raw bytes, so losslessness includes JSON ordering and whitespace—not merely equivalent parsed JSON.

## Interpretation

The trained agent is strongest when new data resembles its representative training samples. Standard codecs may win for small or irregular payloads, because their mature implementations and lower metadata overhead are hard to beat. Run the benchmark against representative production responses before choosing a transport format.

## Layout

- `weather_compression/agent.py` — training, portable agent artifact, runtime encode/decode
- `weather_compression/train_agent.py` — command to create an agent artifact
- `weather_compression/codecs.py` — adaptive research prototype and standard codec implementations
- `weather_compression/sample.py` — deterministic Open-Meteo-style daily fixture
- `weather_compression/benchmark.py` — CLI and comparison report
- `tests/` — exact round-trip tests
