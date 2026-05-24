"""Build and load preprocessed MovieLens-1M artifacts."""
from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import scipy.sparse as sp
import torch

from src.data.movielens import (
    build_user_item_dict,
    download_movielens_1m,
    encode_user_item_features,
    leave_one_out_split,
    load_item_features,
    load_ratings,
    load_user_features,
)
from src.federated import assign_interactions_to_clients, build_item_client_map


def build_knn_hypergraph_edges_split(
    user_features: np.ndarray,
    item_features: np.ndarray,
    num_users: int,
    k: int,
) -> torch.Tensor:
    """Build kNN edges within users and within items separately (same-type only)."""

    def _edges(features: np.ndarray, offset: int = 0) -> List[List[int]]:
        n = features.shape[0]
        norms = np.linalg.norm(features, axis=1, keepdims=True) + 1e-8
        x_norm = features / norms
        sim = x_norm @ x_norm.T
        out: List[List[int]] = []
        for i in range(n):
            sim[i, i] = -1.0
            nn = np.argpartition(-sim[i], min(k, n - 1))[:k]
            for j in nn:
                u, v = offset + i, offset + int(j)
                out.append([u, v])
                out.append([v, u])
        return out

    edges = _edges(user_features, 0) + _edges(item_features, num_users)
    if not edges:
        return torch.zeros((2, 0), dtype=torch.long)
    return torch.tensor(edges, dtype=torch.long).t().contiguous()


def build_bipartite_edges(train_user_items: Dict[int, List[int]], num_users: int) -> torch.Tensor:
    """User-item bipartite edges; item index offset by num_users."""
    src, dst = [], []
    for user, items in train_user_items.items():
        for item in items:
            src.append(user)
            dst.append(num_users + item)
            src.append(num_users + item)
            dst.append(user)
    if not src:
        return torch.zeros((2, 0), dtype=torch.long)
    return torch.tensor([src, dst], dtype=torch.long)


def preprocess_movielens_1m(
    raw_dir: Path,
    processed_dir: Path,
    *,
    min_rating: float = 4.0,
    num_clients: int = 50,
    dirichlet_alpha: float = 1.0,
    attr_knn: int = 10,
    seed: int = 42,
) -> Path:
    """Run full preprocessing pipeline and save to processed_dir."""
    processed_dir.mkdir(parents=True, exist_ok=True)
    out_path = processed_dir / "movielens_1m.pkl"

    data_dir = download_movielens_1m(raw_dir)
    ratings_all = pd_read_ratings_all(data_dir)
    ratings_pos = load_ratings(data_dir, min_rating=min_rating)
    users_df = load_user_features(data_dir)
    movies_df = load_item_features(data_dir)

    # Remap to contiguous ids
    user_ids = sorted(users_df["userId"].unique())
    item_ids = sorted(movies_df["movieId"].unique())
    user_map = {uid: idx for idx, uid in enumerate(user_ids)}
    item_map = {iid: idx for idx, iid in enumerate(item_ids)}

    users_df = users_df[users_df["userId"].isin(user_map)].copy()
    movies_df = movies_df[movies_df["movieId"].isin(item_map)].copy()
    users_df["uid"] = users_df["userId"].map(user_map)
    movies_df["iid"] = movies_df["movieId"].map(item_map)
    users_df = users_df.sort_values("uid").reset_index(drop=True)
    movies_df = movies_df.sort_values("iid").reset_index(drop=True)

    ratings_pos = ratings_pos[
        ratings_pos["userId"].isin(user_map) & ratings_pos["movieId"].isin(item_map)
    ].copy()
    ratings_pos["uid"] = ratings_pos["userId"].map(user_map)
    ratings_pos["iid"] = ratings_pos["movieId"].map(item_map)

    user_items = build_user_item_dict_remapped(ratings_pos)
    train, val, test = leave_one_out_split(user_items, seed=seed)

    user_x, item_x, _, _ = encode_user_item_features(users_df, movies_df)

    num_users = len(user_ids)
    num_items = len(item_ids)
    hyper_edge_index = build_knn_hypergraph_edges_split(user_x, item_x, num_users, attr_knn)
    bi_edge_index = build_bipartite_edges(train, num_users)

    # Item genre prototypes: multi-hot columns as type labels (max genre index per item)
    item_genre_type = item_x.argmax(axis=1).tolist()

    item_to_client = build_item_client_map(
        list(range(num_items)), num_clients, dirichlet_alpha, seed
    )
    client_interactions = assign_interactions_to_clients_remapped(train, item_to_client)

    stats = {
        "num_users": num_users,
        "num_items": num_items,
        "num_interactions_pos": len(ratings_pos),
        "num_interactions_all": len(ratings_all),
        "sparsity_pos_pct": round(
            100 * (1 - len(ratings_pos) / (num_users * num_items)), 2
        ),
        "sparsity_all_pct": round(
            100 * (1 - len(ratings_all) / (num_users * num_items)), 2
        ),
        "min_rating": min_rating,
        "num_clients": num_clients,
        "dirichlet_alpha": dirichlet_alpha,
    }

    artifact: Dict[str, Any] = {
        "stats": stats,
        "num_users": num_users,
        "num_items": num_items,
        "user_x": user_x.astype(np.float32),
        "item_x": item_x.astype(np.float32),
        "item_genre_type": item_genre_type,
        "train": train,
        "val": val,
        "test": test,
        "hyper_edge_index": hyper_edge_index,
        "bi_edge_index": bi_edge_index,
        "item_to_client": item_to_client,
        "client_interactions": client_interactions,
    }

    with open(out_path, "wb") as f:
        pickle.dump(artifact, f)

    meta_path = processed_dir / "movielens_1m_meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    return out_path


def pd_read_ratings_all(data_dir: Path):
    import pandas as pd

    return pd.read_csv(
        data_dir / "ratings.dat",
        sep="::",
        engine="python",
        header=None,
        names=["userId", "movieId", "rating", "timestamp"],
        encoding="latin-1",
    )


def build_user_item_dict_remapped(ratings_pos) -> Dict[int, List[int]]:
    grouped = ratings_pos.groupby("uid")["iid"].apply(list)
    return {int(u): [int(i) for i in items] for u, items in grouped.items()}


def assign_interactions_to_clients_remapped(
    train: Dict[int, List[int]],
    item_to_client: Dict[int, int],
) -> Dict[int, List[Tuple[int, int]]]:
    from collections import defaultdict

    client_data: Dict[int, List[Tuple[int, int]]] = defaultdict(list)
    for user, items in train.items():
        for item in items:
            client = item_to_client.get(item)
            if client is not None:
                client_data[client].append((user, item))
    return dict(client_data)


def load_processed(path: Path) -> Dict[str, Any]:
    with open(path, "rb") as f:
        return pickle.load(f)
