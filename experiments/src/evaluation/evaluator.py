"""Ranking evaluation on held-out test set."""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import torch

from src.metrics import hit_at_k, ndcg_at_k, recall_at_k


@torch.no_grad()
def evaluate_ranking(
    model,
    data: Dict[str, Any],
    user_x: torch.Tensor,
    item_x: torch.Tensor,
    bi_edges: torch.Tensor,
    hyper_edges: torch.Tensor,
    device: torch.device,
    k_list: List[int] | None = None,
    max_users: int | None = 512,
) -> Dict[str, float]:
    """Evaluate on leave-one-out test users."""
    if k_list is None:
        k_list = [10, 20]

    model.eval()
    z_u, z_i, _, _ = model(user_x, item_x, bi_edges, hyper_edges)
    scores = z_u @ z_i.t()

    train = data["train"]
    test = data["test"]
    num_items = data["num_items"]

    test_users = sorted(test.keys())
    if max_users and len(test_users) > max_users:
        rng = np.random.default_rng(42)
        test_users = sorted(rng.choice(test_users, size=max_users, replace=False).tolist())

    metrics: Dict[str, List[float]] = {f"hit@{k}": [] for k in k_list}
    metrics.update({f"ndcg@{k}": [] for k in k_list})
    metrics.update({f"recall@{k}": [] for k in k_list})

    for user in test_users:
        gt_item = test[user]
        row = scores[user].clone()
        # mask training positives
        for it in train.get(user, []):
            row[it] = -1e9
        ranked = torch.argsort(row, descending=True).tolist()
        gt = [gt_item]
        for k in k_list:
            metrics[f"hit@{k}"].append(hit_at_k(ranked, gt, k))
            metrics[f"ndcg@{k}"].append(ndcg_at_k(ranked, gt, k))
            metrics[f"recall@{k}"].append(recall_at_k(ranked, gt, k))

    return {k: float(np.mean(v)) for k, v in metrics.items()}
