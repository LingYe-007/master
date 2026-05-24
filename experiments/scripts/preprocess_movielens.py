#!/usr/bin/env python3
"""Preprocess MovieLens-1M for FedASCL experiments."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.preprocess import preprocess_movielens_1m  # noqa: E402
from src.training.federated_trainer import load_config  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="config/chap3_movielens.yaml",
        help="YAML config with paths and federated settings",
    )
    args = parser.parse_args()

    cfg = load_config(ROOT / args.config)
    out = preprocess_movielens_1m(
        ROOT / cfg["paths"]["data_raw"],
        ROOT / cfg["paths"]["data_processed"],
        min_rating=cfg.get("data", {}).get("min_rating", 4.0),
        num_clients=cfg["federated"]["num_clients"],
        dirichlet_alpha=cfg["federated"]["dirichlet_alpha"],
        attr_knn=cfg.get("fedascl", {}).get("attr_knn", 10),
        seed=cfg["training"]["seed"],
    )
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
