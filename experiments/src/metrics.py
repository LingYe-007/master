"""Recommendation metrics aligned with thesis chapter 2 definitions."""
from __future__ import annotations

import math
from typing import Iterable, Sequence


def hit_at_k(ranked_items: Sequence[int], ground_truth: Iterable[int], k: int) -> float:
    """Hit@K: 1 if any ground-truth item appears in top-K, else 0."""
    gt = set(ground_truth)
    if not gt:
        return 0.0
    top_k = ranked_items[:k]
    return 1.0 if any(item in gt for item in top_k) else 0.0


def recall_at_k(ranked_items: Sequence[int], ground_truth: Iterable[int], k: int) -> float:
    """Recall@K: |GT ∩ top-K| / |GT|."""
    gt = set(ground_truth)
    if not gt:
        return 0.0
    hits = sum(1 for item in ranked_items[:k] if item in gt)
    return hits / len(gt)


def dcg_at_k(relevances: Sequence[float], k: int) -> float:
    """Discounted cumulative gain at K."""
    score = 0.0
    for i, rel in enumerate(relevances[:k]):
        if rel <= 0:
            continue
        score += rel / math.log2(i + 2)
    return score


def ndcg_at_k(ranked_items: Sequence[int], ground_truth: Iterable[int], k: int) -> float:
    """NDCG@K with binary relevance."""
    gt = set(ground_truth)
    if not gt:
        return 0.0
    relevances = [1.0 if item in gt else 0.0 for item in ranked_items[:k]]
    ideal = [1.0] * min(len(gt), k)
    dcg = dcg_at_k(relevances, k)
    idcg = dcg_at_k(ideal, k)
    if idcg == 0:
        return 0.0
    return dcg / idcg


def aggregate_metrics(values: Sequence[float]) -> float:
    """Mean over users; empty input returns 0."""
    if not values:
        return 0.0
    return sum(values) / len(values)
