"""Train and run a fixed, lossless prediction agent for weather payloads."""

from __future__ import annotations

import hashlib
import json
import struct
import zlib
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

_MAGIC = b"WXTA1"
_FINGERPRINT_BYTES = 16


@dataclass(frozen=True)
class WeatherCompressionAgent:
    """A trained lookup table that predicts the next byte from the prior two."""

    predictions: dict[bytes, int]
    training_samples: int

    def predict(self, history: bytearray) -> int:
        if len(history) < 2:
            return history[-1] if history else 0
        return self.predictions.get(bytes(history[-2:]), history[-1])

    def to_bytes(self) -> bytes:
        document = {
            "format": "weather-compression-agent-v1",
            "predictor": "fixed-order-2-byte-context",
            "training_samples": self.training_samples,
            "predictions": {context.hex(): value for context, value in self.predictions.items()},
        }
        return json.dumps(document, separators=(",", ":"), sort_keys=True).encode("utf-8")

    @property
    def fingerprint(self) -> bytes:
        return hashlib.sha256(self.to_bytes()).digest()[:_FINGERPRINT_BYTES]

    def save(self, path: Path) -> None:
        path.write_bytes(self.to_bytes())

    @classmethod
    def load(cls, path: Path) -> "WeatherCompressionAgent":
        document = json.loads(path.read_text(encoding="utf-8"))
        if document.get("format") != "weather-compression-agent-v1":
            raise ValueError("unsupported compression agent format")
        return cls(
            predictions={bytes.fromhex(context): value for context, value in document["predictions"].items()},
            training_samples=document["training_samples"],
        )


def train_agent(samples: list[bytes]) -> WeatherCompressionAgent:
    """Create a fixed predictor from representative historical API samples."""
    if not samples:
        raise ValueError("at least one training sample is required")
    counts: dict[bytes, Counter[int]] = defaultdict(Counter)
    for sample in samples:
        for index in range(2, len(sample)):
            counts[sample[index - 2 : index]][sample[index]] += 1
    predictions = {
        context: max(options.items(), key=lambda item: (item[1], item[0]))[0]
        for context, options in counts.items()
    }
    return WeatherCompressionAgent(predictions=predictions, training_samples=len(samples))


def compress_with_agent(data: bytes, agent: WeatherCompressionAgent) -> bytes:
    """Encode a payload using a pre-trained, immutable prediction agent."""
    history = bytearray()
    residuals = bytearray()
    for value in data:
        residuals.append((value - agent.predict(history)) & 0xFF)
        history.append(value)
    header = _MAGIC + agent.fingerprint + struct.pack(">Q", len(data))
    return header + zlib.compress(bytes(residuals), level=9)


def decompress_with_agent(payload: bytes, agent: WeatherCompressionAgent) -> bytes:
    """Deterministically reconstruct exact bytes with the matching agent."""
    header_size = len(_MAGIC) + _FINGERPRINT_BYTES + 8
    if not payload.startswith(_MAGIC) or len(payload) < header_size:
        raise ValueError("not a trained weather-agent payload")
    fingerprint = payload[len(_MAGIC) : len(_MAGIC) + _FINGERPRINT_BYTES]
    if fingerprint != agent.fingerprint:
        raise ValueError("payload was compressed with a different agent")
    expected_length = struct.unpack(">Q", payload[len(_MAGIC) + _FINGERPRINT_BYTES : header_size])[0]
    residuals = zlib.decompress(payload[header_size:])
    if len(residuals) != expected_length:
        raise ValueError("corrupt trained weather-agent payload")
    history = bytearray()
    for residual in residuals:
        history.append((agent.predict(history) + residual) & 0xFF)
    return bytes(history)
