"""Federated data partitioning utilities."""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Sequence, Tuple

import numpy as np


def dirichlet_partition(
    item_ids: Sequence[int],
    num_clients: int,
    alpha: float,
    seed: int = 42,
) -> Dict[int, List[int]]:
    """
    Assign items to clients via Dirichlet distribution (Non-IID by item).
    Returns mapping client_id -> list of item indices assigned to that client.
    Used to split interaction data in federated recommendation.
    """
    rng = np.random.default_rng(seed)
    num_items = len(item_ids)
    if alpha == float("inf"):
        # IID: round-robin
        client_items: Dict[int, List[int]] = defaultdict(list)
        for idx, item in enumerate(item_ids):
            client_items[idx % num_clients].append(int(item))
        return dict(client_items)

    proportions = rng.dirichlet([alpha] * num_clients, size=num_items)
    client_items = defaultdict(list)
    for item_idx, item in enumerate(item_ids):
        owner = int(np.argmax(proportions[item_idx]))
        client_items[owner].append(int(item))
    return dict(client_items)


def assign_interactions_to_clients(
    user_items: Dict[int, List[int]],
    item_to_client: Dict[int, int],
) -> Dict[int, List[Tuple[int, int]]]:
    """
    Map (user, item) interactions to clients based on item ownership.
    Returns client_id -> list of (user_id, item_id).
    """
    client_data: Dict[int, List[Tuple[int, int]]] = defaultdict(list)
    for user, items in user_items.items():
        for item in items:
            client = item_to_client.get(item)
            if client is not None:
                client_data[client].append((user, item))
    return dict(client_data)


def build_item_client_map(
    item_ids: Sequence[int],
    num_clients: int,
    alpha: float,
    seed: int = 42,
) -> Dict[int, int]:
    """item_id -> client_id."""
    partition = dirichlet_partition(item_ids, num_clients, alpha, seed)
    mapping: Dict[int, int] = {}
    for client_id, items in partition.items():
        for item in items:
            mapping[item] = client_id
    return mapping


def sample_participating_clients(
    num_clients: int,
    participation_rate: float,
    rng: np.random.Generator,
) -> List[int]:
    """Random subset of clients for one federated round."""
    k = max(1, int(round(num_clients * participation_rate)))
    k = min(k, num_clients)
    return sorted(rng.choice(num_clients, size=k, replace=False).tolist())
