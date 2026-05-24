"""Federated training loop for FedASCL."""
from __future__ import annotations

import copy
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import torch
import torch.optim as optim
import yaml
from tqdm import tqdm

from src.data.bpr_dataset import build_user_positive_set, sample_negative_items
from src.data.preprocess import load_processed, preprocess_movielens_1m
from src.evaluation.evaluator import evaluate_ranking
from src.federated import sample_participating_clients
from src.models.fedascl import FedASCL, aggregate_prototypes


class FederatedTrainer:
    def __init__(self, config: Dict[str, Any], device: torch.device) -> None:
        self.cfg = config
        self.device = device
        self.rng = np.random.default_rng(config["training"]["seed"])

        raw_dir = Path(config["paths"]["data_raw"])
        proc_dir = Path(config["paths"]["data_processed"])
        pkl = proc_dir / "movielens_1m.pkl"
        if not pkl.exists():
            preprocess_movielens_1m(
                raw_dir,
                proc_dir,
                min_rating=config.get("data", {}).get("min_rating", 4.0),
                num_clients=config["federated"]["num_clients"],
                dirichlet_alpha=config["federated"]["dirichlet_alpha"],
                attr_knn=config.get("fedascl", {}).get("attr_knn", 10),
                seed=config["training"]["seed"],
            )
        self.data = load_processed(pkl)

        self.user_x = torch.tensor(self.data["user_x"], device=device)
        self.item_x = torch.tensor(self.data["item_x"], device=device)
        self.bi_edges = self.data["bi_edge_index"].to(device)
        self.hyper_edges = self.data["hyper_edge_index"].to(device)
        self.item_types = torch.tensor(self.data["item_genre_type"], dtype=torch.long, device=device)

        num_proto = int(self.item_x.shape[1]) if self.item_x.shape[1] > 0 else 20
        num_proto = max(num_proto, config.get("fedascl", {}).get("num_prototypes", 20))

        self.model = FedASCL(
            num_users=self.data["num_users"],
            num_items=self.data["num_items"],
            user_attr_dim=self.data["user_x"].shape[1],
            item_attr_dim=self.data["item_x"].shape[1],
            embed_dim=config["training"]["embed_dim"],
            num_prototypes=min(num_proto, 64),
        ).to(device)

        self.global_prototypes = self.model.prototype_emb.weight.data.clone()
        self.user_pos = build_user_positive_set(self.data["train"])
        self.results_dir = Path(config["paths"]["results"])
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def _local_train(
        self,
        client_id: int,
        global_state: Dict[str, torch.Tensor],
        global_prototypes: torch.Tensor,
    ) -> tuple:
        model = copy.deepcopy(self.model)
        model.load_state_dict(global_state)
        model.train()

        interactions = self.data["client_interactions"].get(client_id, [])
        if not interactions:
            return model.state_dict(), None, None

        lr = self.cfg["training"]["lr"]
        opt = optim.Adam(model.parameters(), lr=lr)
        fedascl_cfg = self.cfg.get("fedascl", {})
        tau_cl = fedascl_cfg.get("tau_cl", 0.2)
        tau_proto = fedascl_cfg.get("tau_proto", 0.5)
        lam_cl = fedascl_cfg.get("lambda_cl", 0.1)
        lam_proto = fedascl_cfg.get("lambda_proto", 0.1)
        batch_size = self.cfg["training"]["batch_size"]
        local_epochs = self.cfg["federated"]["local_epochs"]

        pairs = interactions
        local_items = torch.tensor(sorted({i for _, i in pairs}), device=self.device)

        for _ in range(local_epochs):
            self.rng.shuffle(pairs)
            for start in range(0, len(pairs), batch_size):
                batch = pairs[start : start + batch_size]
                users = torch.tensor([u for u, _ in batch], dtype=torch.long, device=self.device)
                pos = torch.tensor([i for _, i in batch], dtype=torch.long, device=self.device)
                neg = sample_negative_items(
                    users, pos, self.user_pos, self.data["num_items"], self.rng
                )

                z_u, z_i, z_stru, z_attr = model(
                    self.user_x, self.item_x, self.bi_edges, self.hyper_edges
                )
                loss_bpr = model.bpr_loss(users, pos, neg, z_u, z_i)

                n_u = self.data["num_users"]
                node_idx = torch.cat([users, n_u + pos], dim=0)
                loss_cl = model.info_nce_loss(z_stru, z_attr, node_idx, tau=tau_cl)

                # Prototype alignment on item nodes in batch
                loss_proto = model.prototype_loss(
                    z_i,
                    pos,
                    self.item_types[pos],
                    global_prototypes,
                    tau_p=tau_proto,
                )

                loss = loss_bpr + lam_cl * loss_cl + lam_proto * loss_proto
                opt.zero_grad()
                loss.backward()
                opt.step()

        with torch.no_grad():
            z_u, z_i, _, _ = model(self.user_x, self.item_x, self.bi_edges, self.hyper_edges)
            proto_sum, proto_cnt = model.compute_local_prototypes(
                z_i, self.item_types, local_items
            )

        return model.state_dict(), proto_sum, proto_cnt

    def train(self) -> Dict[str, Any]:
        cfg = self.cfg
        num_clients = cfg["federated"]["num_clients"]
        rounds = cfg["federated"]["global_rounds"]
        part_rate = cfg["federated"]["participation_rate"]
        eval_every = cfg["evaluation"]["eval_every"]

        history: List[Dict[str, float]] = []
        global_state = self.model.state_dict()

        for rnd in tqdm(range(1, rounds + 1), desc="Fed rounds"):
            participants = sample_participating_clients(num_clients, part_rate, self.rng)
            client_states = []
            proto_sums, proto_cnts = [], []

            for cid in participants:
                state, ps, pc = self._local_train(cid, global_state, self.global_prototypes)
                client_states.append(state)
                if ps is not None:
                    proto_sums.append(ps)
                    proto_cnts.append(pc)

            # FedAvg
            avg_state = copy.deepcopy(global_state)
            for key in avg_state:
                avg_state[key] = torch.stack(
                    [cs[key].float() for cs in client_states], dim=0
                ).mean(dim=0)
            global_state = avg_state
            self.model.load_state_dict(global_state)

            if proto_sums:
                self.global_prototypes = aggregate_prototypes(
                    proto_sums,
                    proto_cnts,
                    self.model.num_prototypes,
                    self.model.embed_dim,
                    self.device,
                )
                self.model.prototype_emb.weight.data.copy_(self.global_prototypes)

            if rnd % eval_every == 0 or rnd == rounds:
                metrics = evaluate_ranking(
                    self.model,
                    self.data,
                    self.user_x,
                    self.item_x,
                    self.bi_edges,
                    self.hyper_edges,
                    self.device,
                    k_list=[10, 20],
                )
                row = {"round": rnd, **metrics}
                history.append(row)
                tqdm.write(
                    f"Round {rnd}: Hit@10={metrics['hit@10']:.4f} "
                    f"NDCG@10={metrics['ndcg@10']:.4f}"
                )

        out = {
            "config": cfg,
            "history": history,
            "stats": self.data["stats"],
        }
        out_path = self.results_dir / f"{cfg['experiment_id']}_results.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        return out


def load_config(path: Path) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_from_config(config_path: Path) -> Dict[str, Any]:
    cfg = load_config(config_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    trainer = FederatedTrainer(cfg, device)
    return trainer.train()
