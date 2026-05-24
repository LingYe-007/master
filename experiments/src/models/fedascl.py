"""FedASCL model (simplified faithful implementation for reproduction)."""
from __future__ import annotations

import math
from typing import Dict, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv


class FedASCL(nn.Module):
    """
    Dual-view federated recommender:
    - Structure view: bipartite GraphSAGE on user-item graph
    - Attribute view: MLP + hypergraph neighbor mean
    - Meta-path attention fuses two views
    - Losses: BPR + InfoNCE + prototype alignment
    """

    def __init__(
        self,
        num_users: int,
        num_items: int,
        user_attr_dim: int,
        item_attr_dim: int,
        embed_dim: int = 64,
        num_prototypes: int = 20,
    ) -> None:
        super().__init__()
        self.num_users = num_users
        self.num_items = num_items
        self.embed_dim = embed_dim
        self.num_prototypes = num_prototypes

        self.user_id_emb = nn.Embedding(num_users, embed_dim)
        self.item_id_emb = nn.Embedding(num_items, embed_dim)
        nn.init.xavier_uniform_(self.user_id_emb.weight)
        nn.init.xavier_uniform_(self.item_id_emb.weight)

        self.user_attr_mlp = nn.Sequential(
            nn.Linear(user_attr_dim, embed_dim),
            nn.ReLU(),
            nn.Linear(embed_dim, embed_dim),
        )
        self.item_attr_mlp = nn.Sequential(
            nn.Linear(item_attr_dim, embed_dim),
            nn.ReLU(),
            nn.Linear(embed_dim, embed_dim),
        )

        self.stru_conv1 = SAGEConv(embed_dim, embed_dim)
        self.stru_conv2 = SAGEConv(embed_dim, embed_dim)

        self.attn_W = nn.Linear(embed_dim, embed_dim)
        self.attn_q = nn.Parameter(torch.randn(embed_dim))

        self.prototype_emb = nn.Embedding(num_prototypes, embed_dim)
        nn.init.xavier_uniform_(self.prototype_emb.weight)

    def encode_attribute(
        self,
        user_x: torch.Tensor,
        item_x: torch.Tensor,
        hyper_edge_index: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        n_u = self.num_users
        id_emb = torch.cat([self.user_id_emb.weight, self.item_id_emb.weight], dim=0)
        attr_raw = torch.cat(
            [self.user_attr_mlp(user_x), self.item_attr_mlp(item_x)], dim=0
        )
        z = id_emb + attr_raw

        if hyper_edge_index.numel() > 0:
            src, dst = hyper_edge_index
            agg = torch.zeros_like(z)
            count = torch.zeros(z.size(0), device=z.device)
            agg.index_add_(0, dst, z[src])
            count.index_add_(0, dst, torch.ones(dst.size(0), device=z.device))
            count = count.clamp(min=1).unsqueeze(-1)
            z = z + agg / count

        return z[:n_u], z[n_u:]

    def encode_structure(self, bi_edge_index: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        n_u = self.num_users
        x = torch.cat([self.user_id_emb.weight, self.item_id_emb.weight], dim=0)
        if bi_edge_index.numel() == 0:
            return x[:n_u], x[n_u:]
        h = F.relu(self.stru_conv1(x, bi_edge_index))
        h = self.stru_conv2(h, bi_edge_index)
        return h[:n_u], h[n_u:]

    def fuse_views(
        self,
        z_stru_u: torch.Tensor,
        z_stru_i: torch.Tensor,
        z_attr_u: torch.Tensor,
        z_attr_i: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        def path_weight(z: torch.Tensor) -> torch.Tensor:
            score = torch.tanh(self.attn_W(z)) @ self.attn_q
            return score.mean()

        w_stru = path_weight(torch.cat([z_stru_u, z_stru_i], dim=0))
        w_attr = path_weight(torch.cat([z_attr_u, z_attr_i], dim=0))
        beta = torch.softmax(torch.stack([w_stru, w_attr]), dim=0)

        z_u = beta[0] * z_stru_u + beta[1] * z_attr_u
        z_i = beta[0] * z_stru_i + beta[1] * z_attr_i
        return z_u, z_i, torch.cat([z_stru_u, z_stru_i]), torch.cat([z_attr_u, z_attr_i])

    def forward(
        self,
        user_x: torch.Tensor,
        item_x: torch.Tensor,
        bi_edge_index: torch.Tensor,
        hyper_edge_index: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        z_stru_u, z_stru_i = self.encode_structure(bi_edge_index)
        z_attr_u, z_attr_i = self.encode_attribute(user_x, item_x, hyper_edge_index)
        return self.fuse_views(z_stru_u, z_stru_i, z_attr_u, z_attr_i)

    def predict(
        self,
        users: torch.Tensor,
        items: torch.Tensor,
        z_u: torch.Tensor,
        z_i: torch.Tensor,
    ) -> torch.Tensor:
        return (z_u[users] * z_i[items]).sum(dim=-1)

    def bpr_loss(
        self,
        users: torch.Tensor,
        pos_items: torch.Tensor,
        neg_items: torch.Tensor,
        z_u: torch.Tensor,
        z_i: torch.Tensor,
    ) -> torch.Tensor:
        pos = self.predict(users, pos_items, z_u, z_i)
        neg = self.predict(users, neg_items, z_u, z_i)
        return -F.logsigmoid(pos - neg).mean()

    def info_nce_loss(
        self,
        z_stru: torch.Tensor,
        z_attr: torch.Tensor,
        node_idx: torch.Tensor,
        tau: float = 0.2,
    ) -> torch.Tensor:
        s = F.normalize(z_stru[node_idx], dim=-1)
        a = F.normalize(z_attr[node_idx], dim=-1)
        logits = s @ a.t() / tau
        labels = torch.arange(logits.size(0), device=logits.device)
        return F.cross_entropy(logits, labels)

    def prototype_loss(
        self,
        z_nodes: torch.Tensor,
        node_idx: torch.Tensor,
        type_labels: torch.Tensor,
        global_prototypes: torch.Tensor,
        tau_p: float = 0.5,
    ) -> torch.Tensor:
        z = F.normalize(z_nodes[node_idx], dim=-1)
        proto = F.normalize(global_prototypes, dim=-1)
        logits = z @ proto.t() / tau_p
        return F.cross_entropy(logits, type_labels)

    def compute_local_prototypes(
        self,
        z_items: torch.Tensor,
        item_types: torch.Tensor,
        local_item_ids: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Weighted prototype vectors for items present on client."""
        k = self.num_prototypes
        proto_sum = torch.zeros(k, self.embed_dim, device=z_items.device)
        proto_cnt = torch.zeros(k, device=z_items.device)
        for idx in local_item_ids.tolist():
            t = int(item_types[idx].item())
            proto_sum[t] += z_items[idx]
            proto_cnt[t] += 1
        return proto_sum, proto_cnt


def aggregate_prototypes(
    client_sums: list,
    client_counts: list,
    num_prototypes: int,
    embed_dim: int,
    device: torch.device,
) -> torch.Tensor:
    total_sum = torch.zeros(num_prototypes, embed_dim, device=device)
    total_cnt = torch.zeros(num_prototypes, device=device)
    for s, c in zip(client_sums, client_counts):
        total_sum += s.to(device)
        total_cnt += c.to(device)
    total_cnt = total_cnt.clamp(min=1).unsqueeze(-1)
    return total_sum / total_cnt
