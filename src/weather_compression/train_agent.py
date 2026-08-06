"""Create a reusable trained agent artifact from representative weather payloads."""

from __future__ import annotations

import argparse
from pathlib import Path

from .agent import train_agent
from .sample import historical_weather_samples


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a fixed lossless weather compression agent.")
    parser.add_argument("--output", type=Path, default=Path("weather-agent.json"), help="Agent artifact destination")
    parser.add_argument("samples", nargs="*", type=Path, help="Representative historical raw JSON payloads")
    args = parser.parse_args()
    samples = [path.read_bytes() for path in args.samples] or historical_weather_samples()
    agent = train_agent(samples)
    agent.save(args.output)
    print(f"Saved agent trained on {agent.training_samples} samples to {args.output}")
    print(f"Agent fingerprint: {agent.fingerprint.hex()}")


if __name__ == "__main__":
    main()
