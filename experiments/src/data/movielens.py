"""MovieLens-1M loading and preprocessing (thesis chap3 tables)."""
from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import requests
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder

ML1M_URL = "https://files.grouplens.org/datasets/movielens/ml-1m.zip"


def download_movielens_1m(raw_dir: Path) -> Path:
    """Download and extract MovieLens-1M; return extract root."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    zip_path = raw_dir / "ml-1m.zip"
    extract_dir = raw_dir / "ml-1m"

    if extract_dir.exists() and (extract_dir / "ratings.dat").exists():
        return extract_dir

    if not zip_path.exists():
        print(f"Downloading MovieLens-1M -> {zip_path}")
        resp = requests.get(ML1M_URL, stream=True, timeout=120)
        resp.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                f.write(chunk)

    print(f"Extracting {zip_path}")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(raw_dir)
    return extract_dir


def load_ratings(data_dir: Path, min_rating: float = 4.0) -> pd.DataFrame:
    """Load ratings and binarize (>= min_rating as positive)."""
    ratings = pd.read_csv(
        data_dir / "ratings.dat",
        sep="::",
        engine="python",
        header=None,
        names=["userId", "movieId", "rating", "timestamp"],
        encoding="latin-1",
    )
    ratings = ratings[ratings["rating"] >= min_rating].copy()
    return ratings


def load_user_features(data_dir: Path) -> pd.DataFrame:
    users = pd.read_csv(
        data_dir / "users.dat",
        sep="::",
        engine="python",
        header=None,
        names=["userId", "Gender", "Age", "Occupation", "Zip-code"],
        encoding="latin-1",
    )
    return users


def load_item_features(data_dir: Path) -> pd.DataFrame:
    movies = pd.read_csv(
        data_dir / "movies.dat",
        sep="::",
        engine="python",
        header=None,
        names=["movieId", "Title", "Genres"],
        encoding="latin-1",
    )
    movies["Genres"] = movies["Genres"].str.split("|")
    return movies


def build_user_item_dict(ratings: pd.DataFrame) -> Dict[int, List[int]]:
    grouped = ratings.groupby("userId")["movieId"].apply(list)
    return {int(u): [int(i) for i in items] for u, items in grouped.items()}


def leave_one_out_split(
    user_items: Dict[int, List[int]],
    seed: int = 42,
) -> Tuple[Dict[int, List[int]], Dict[int, int], Dict[int, int]]:
    """
    For each user, hold out one random positive for test; one for val if len>=2.
    Returns train dict, val dict (user->item), test dict (user->item).
    """
    rng = np.random.default_rng(seed)
    train: Dict[int, List[int]] = {}
    val: Dict[int, int] = {}
    test: Dict[int, int] = {}

    for user, items in user_items.items():
        if len(items) < 2:
            train[user] = items[:]
            continue
        shuffled = items[:]
        rng.shuffle(shuffled)
        test[user] = shuffled[0]
        val[user] = shuffled[1]
        train[user] = shuffled[2:]
    return train, val, test


def encode_user_item_features(
    users: pd.DataFrame,
    movies: pd.DataFrame,
) -> Tuple[np.ndarray, np.ndarray, Dict[int, int], Dict[int, int]]:
    """One-hot user attrs + multi-hot genres; return arrays and id maps."""
    user_enc = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    user_x = user_enc.fit_transform(users[["Gender", "Age", "Occupation"]])

    mlb = MultiLabelBinarizer()
    genre_x = mlb.fit_transform(movies["Genres"])

    user_id_map = {uid: idx for idx, uid in enumerate(users["userId"].tolist())}
    item_id_map = {iid: idx for idx, iid in enumerate(movies["movieId"].tolist())}

    return user_x, genre_x, user_id_map, item_id_map


def dataset_statistics(ratings: pd.DataFrame, users: pd.DataFrame, movies: pd.DataFrame) -> dict:
    n_users = users["userId"].nunique()
    n_items = movies["movieId"].nunique()
    n_inter = len(ratings)
    sparsity = 1.0 - n_inter / (n_users * n_items)
    return {
        "num_users": int(n_users),
        "num_items": int(n_items),
        "num_interactions": int(n_inter),
        "sparsity_pct": round(sparsity * 100, 2),
    }
