#!/usr/bin/env python3
"""
Phase 0 smoke test: environment, data download, metrics, federated split.
Run from experiments/:  python scripts/smoke_test.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import yaml

from src.data.movielens import (
    build_user_item_dict,
    dataset_statistics,
    download_movielens_1m,
    leave_one_out_split,
    load_item_features,
    load_ratings,
    load_user_features,
)
from src.federated import build_item_client_map, sample_participating_clients
from src.metrics import hit_at_k, ndcg_at_k, recall_at_k


def check_torch() -> None:
    import torch

    print(f"PyTorch {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")


def check_metrics() -> None:
    ranked = [3, 1, 5, 2, 4]
    gt = [2, 5]
    assert hit_at_k(ranked, gt, 3) == 1.0
    assert recall_at_k(ranked, gt, 3) == 0.5
    assert ndcg_at_k(ranked, gt, 5) > 0.0
    print("metrics: OK")


def check_movielens() -> dict:
    raw = ROOT / "data" / "raw"
    data_dir = download_movielens_1m(raw)
    ratings = load_ratings(data_dir)
    users = load_user_features(data_dir)
    movies = load_item_features(data_dir)
    stats = dataset_statistics(ratings, users, movies)
    print(f"MovieLens-1M: users={stats['num_users']}, items={stats['num_items']}, "
          f"interactions={stats['num_interactions']}, sparsity={stats['sparsity_pct']}%")

    # Thesis table: 6040 users, 3706 items, 95.53% sparsity (after binarization counts differ slightly)
    user_items = build_user_item_dict(ratings)
    train, val, test = leave_one_out_split(user_items, seed=42)
    print(f"split: train_users={len(train)}, val={len(val)}, test={len(test)}")

    item_ids = movies["movieId"].tolist()
    item_map = build_item_client_map(item_ids, num_clients=50, alpha=1.0, seed=42)
    rng = np.random.default_rng(42)
    participants = sample_participating_clients(50, 0.2, rng)
    print(f"federated: item_map={len(item_map)} items, round_participants={len(participants)}")
    return stats


def check_config() -> None:
    cfg_path = ROOT / "config" / "chap3_movielens.yaml"
    with open(cfg_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    assert cfg["federated"]["num_clients"] == 50
    assert cfg["training"]["seed"] == 42
    print(f"config chap3: OK ({cfg['experiment_id']})")


def main() -> None:
    print("=== FedASCL reproduction smoke test ===\n")
    check_torch()
    print()
    check_metrics()
    print()
    check_config()
    print()
    stats = check_movielens()
    print("\n=== ALL CHECKS PASSED ===")
    print("Next: Phase 2 — implement FedASCL model (see REPRODUCTION_PLAN.md)")


if __name__ == "__main__":
    main()
