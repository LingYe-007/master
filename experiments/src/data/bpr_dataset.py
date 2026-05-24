"""PyTorch Dataset helpers for BPR training."""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import numpy as np
import torch
from torch.utils.data import Dataset


class BPRDataset(Dataset):
    """Sample (user, pos_item, neg_item) triplets."""

    def __init__(
        self,
        user_items: Dict[int, List[int]],
        num_items: int,
        num_neg: int = 1,
        seed: int = 42,
    ) -> None:
        self.pairs: List[Tuple[int, int]] = []
        for user, items in user_items.items():
            for item in items:
                self.pairs.append((user, item))
        self.num_items = num_items
        self.num_neg = num_neg
        self.rng = np.random.default_rng(seed)

    def __len__(self) -> int:
        return len(self.pairs)

    def __getitem__(self, idx: int) -> Tuple[int, int, int]:
        user, pos = self.pairs[idx]
        while True:
            neg = int(self.rng.integers(0, self.num_items))
            # caller should ensure neg not in user's items via separate set if needed
            if neg != pos:
                break
        return user, pos, neg


def collate_bpr(batch: Sequence[Tuple[int, int, int]]) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    users, pos, neg = zip(*batch)
    return (
        torch.tensor(users, dtype=torch.long),
        torch.tensor(pos, dtype=torch.long),
        torch.tensor(neg, dtype=torch.long),
    )


def build_user_positive_set(user_items: Dict[int, List[int]]) -> Dict[int, set]:
    return {u: set(items) for u, items in user_items.items()}


def sample_negative_items(
    users: torch.Tensor,
    pos_items: torch.Tensor,
    user_pos_sets: Dict[int, set],
    num_items: int,
    rng: np.random.Generator,
) -> torch.Tensor:
    """Sample negatives not in user's training positives."""
    negs = []
    for u, p in zip(users.tolist(), pos_items.tolist()):
        for _ in range(32):
            n = int(rng.integers(0, num_items))
            if n != p and n not in user_pos_sets.get(u, set()):
                negs.append(n)
                break
        else:
            negs.append((p + 1) % num_items)
    return torch.tensor(negs, dtype=torch.long)
