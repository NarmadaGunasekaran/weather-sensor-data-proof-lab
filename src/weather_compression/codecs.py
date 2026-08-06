"""Fully lossless codecs used by the weather payload benchmark."""

from __future__ import annotations

import bz2
import gzip
import lzma
import struct
import zlib
from collections import Counter, defaultdict
from collections.abc import Callable

Codec = tuple[Callable[[bytes], bytes], Callable[[bytes], bytes]]
_MAGIC = b"WXAI1"


def _predict(contexts: dict[bytes, Counter[int]], history: bytearray) -> int:
    if len(history) < 2:
        return history[-1] if history else 0
    options = contexts.get(bytes(history[-2:]))
    if not options:
        return history[-1]
    return max(options.items(), key=lambda item: (item[1], item[0]))[0]


def _learn(contexts: dict[bytes, Counter[int]], history: bytearray, value: int) -> None:
    if len(history) >= 2:
        contexts[bytes(history[-2:])][value] += 1


def adaptive_compress(data: bytes) -> bytes:
    """Encode exact byte residuals against a learned order-2 predictor."""
    contexts: dict[bytes, Counter[int]] = defaultdict(Counter)
    history = bytearray()
    residuals = bytearray()
    for value in data:
        prediction = _predict(contexts, history)
        residuals.append((value - prediction) & 0xFF)
        _learn(contexts, history, value)
        history.append(value)
    return _MAGIC + struct.pack(">Q", len(data)) + zlib.compress(bytes(residuals), level=9)


def adaptive_decompress(payload: bytes) -> bytes:
    """Recreate the original bytes using the same adaptive predictor."""
    if not payload.startswith(_MAGIC) or len(payload) < len(_MAGIC) + 8:
        raise ValueError("not an adaptive weather payload")
    expected_length = struct.unpack(">Q", payload[len(_MAGIC) : len(_MAGIC) + 8])[0]
    residuals = zlib.decompress(payload[len(_MAGIC) + 8 :])
    if len(residuals) != expected_length:
        raise ValueError("corrupt adaptive weather payload")

    contexts: dict[bytes, Counter[int]] = defaultdict(Counter)
    history = bytearray()
    for residual in residuals:
        value = (_predict(contexts, history) + residual) & 0xFF
        _learn(contexts, history, value)
        history.append(value)
    return bytes(history)


CODECS: dict[str, Codec] = {
    "adaptive-predictor": (adaptive_compress, adaptive_decompress),
    "zlib-9": (lambda data: zlib.compress(data, level=9), zlib.decompress),
    "gzip-9": (lambda data: gzip.compress(data, compresslevel=9, mtime=0), gzip.decompress),
    "bz2-9": (lambda data: bz2.compress(data, compresslevel=9), bz2.decompress),
    "lzma-9": (lambda data: lzma.compress(data, preset=9), lzma.decompress),
}
