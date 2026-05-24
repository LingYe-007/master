#!/usr/bin/env python3
"""Download MovieLens-1M into experiments/data/raw/."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.movielens import download_movielens_1m  # noqa: E402


def main() -> None:
    raw_dir = ROOT / "data" / "raw"
    extract_dir = download_movielens_1m(raw_dir)
    print(f"OK: {extract_dir}")


if __name__ == "__main__":
    main()
