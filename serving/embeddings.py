"""Embedding layer with the same strategy pattern as extraction.

- ``SentenceTransformerEmbedder`` — production path (all-MiniLM-L6-v2, 384-dim).
- ``HashingEmbedder`` — deterministic, dependency-free fallback so CI and tests
  never download models. Not semantically meaningful; identical interface.
"""

from __future__ import annotations

import hashlib
import math
from typing import Protocol


class Embedder(Protocol):
    name: str
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class HashingEmbedder:
    """Deterministic feature-hashing embedder (test/CI fallback)."""

    name = "hashing"
    dim = 384

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for text in texts:
            vec = [0.0] * self.dim
            for token in text.lower().split():
                h = int(hashlib.md5(token.encode()).hexdigest(), 16)
                vec[h % self.dim] += 1.0 if (h >> 128) % 2 else -1.0
            norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            vectors.append([v / norm for v in vec])
        return vectors


class SentenceTransformerEmbedder:
    name = "all-MiniLM-L6-v2"
    dim = 384

    def __init__(self) -> None:
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts, normalize_embeddings=True).tolist()


def get_embedder() -> Embedder:
    try:
        import sentence_transformers  # noqa: F401

        return SentenceTransformerEmbedder()
    except ImportError:
        return HashingEmbedder()
