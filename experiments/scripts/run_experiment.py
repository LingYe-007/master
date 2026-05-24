#!/usr/bin/env python3
"""Run FedASCL federated experiment from YAML config."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.training.federated_trainer import run_from_config  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Run FedASCL experiment")
    parser.add_argument(
        "--config",
        default="config/chap3_movielens_smoke.yaml",
        help="Path to experiment YAML (relative to experiments/)",
    )
    args = parser.parse_args()
    config_path = ROOT / args.config
    if not config_path.exists():
        raise FileNotFoundError(config_path)
    results = run_from_config(config_path)
    print("\nDone. Final metrics:")
    if results["history"]:
        print(results["history"][-1])


if __name__ == "__main__":
    main()
