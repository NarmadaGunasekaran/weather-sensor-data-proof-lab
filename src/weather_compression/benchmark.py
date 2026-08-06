"""CLI to compare lossless compression choices for a weather API response."""

from __future__ import annotations

import argparse
import hashlib
import time
from pathlib import Path

from .agent import compress_with_agent, decompress_with_agent, train_agent
from .codecs import CODECS
from .sample import historical_weather_samples, one_day_weather_payload


def benchmark(data: bytes) -> list[dict[str, object]]:
    source_hash = hashlib.sha256(data).hexdigest()
    agent = train_agent(historical_weather_samples())
    codecs = {
        "trained-weather-agent": (
            lambda payload: compress_with_agent(payload, agent),
            lambda payload: decompress_with_agent(payload, agent),
        ),
        **CODECS,
    }
    results: list[dict[str, object]] = []
    for name, (compress, decompress) in codecs.items():
        started = time.perf_counter()
        compressed = compress(data)
        compress_ms = (time.perf_counter() - started) * 1_000
        started = time.perf_counter()
        restored = decompress(compressed)
        decompress_ms = (time.perf_counter() - started) * 1_000
        if hashlib.sha256(restored).hexdigest() != source_hash:
            raise RuntimeError(f"{name} failed the exact lossless round trip")
        results.append(
            {
                "name": name,
                "bytes": len(compressed),
                "ratio": len(compressed) / len(data),
                "saved": 1 - len(compressed) / len(data),
                "compress_ms": compress_ms,
                "decompress_ms": decompress_ms,
            }
        )
    return sorted(results, key=lambda result: result["bytes"])


def render_report(data: bytes, results: list[dict[str, object]]) -> str:
    lines = [
        "# Weather API Lossless Compression Report",
        "",
        f"Original payload: **{len(data):,} bytes**  ",
        f"SHA-256: `{hashlib.sha256(data).hexdigest()}`",
        "",
        "| Codec | Compressed bytes | Ratio | Saved | Compress | Decompress | Exact round trip |",
        "| --- | ---: | ---: | ---: | ---: | ---: | :---: |",
    ]
    for result in results:
        lines.append(
            "| {name} | {bytes:,} | {ratio:.3f}x | {saved:.1%} | {compress_ms:.2f} ms | "
            "{decompress_ms:.2f} ms | yes |".format(**result)
        )
    lines.extend(
        [
            "",
            "`trained-weather-agent` follows a train-once, compress-anywhere workflow: a fixed prediction "
            "profile is learned from seven historical samples, then used at runtime. All methods preserve raw input bytes.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare lossless weather API compression codecs.")
    parser.add_argument("input", nargs="?", type=Path, help="Raw one-day weather API JSON response")
    parser.add_argument("--output", type=Path, help="Optional Markdown report path")
    args = parser.parse_args()
    data = args.input.read_bytes() if args.input else one_day_weather_payload()
    report = render_report(data, benchmark(data))
    print(report)
    if args.output:
        args.output.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
