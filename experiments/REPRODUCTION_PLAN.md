# FedASCL 论文实验复现计划书

> 基于当前论文（第三、四、五章）与仓库现状编制。  
> 环境：Python 3.12、NVIDIA RTX 4060 Laptop GPU（8GB）。

---

## 0. 现状审计（2026-05-24）

| 项目 | 状态 |
|------|------|
| 论文 LaTeX（chap3/4/5） | ✅ 完整 |
| FedASCL 训练代码 | ❌ **不存在** |
| 实验数值来源 | `scripts/generate_figures.py` 硬编码，与 tex 主表对齐 |
| 前端原型 `fedrec-frontend` | ✅ 存在，**mock API**，非真实训练 |
| GPU | RTX 4060 8GB |

**结论**：复现 ≠ 改图，需从零搭建 `experiments/` 训练流水线。  
**目标**：产出可运行的联邦训练代码 + 真实 log/CSV；**不保证**与论文表格逐位一致（真实实验会有偏差）。

---

## 1. 实验清单（与论文对应）

### 第三章（`tab:exp_config_chap3`）

| ID | 实验 | 数据集 | 关键设定 | 输出 |
|----|------|--------|----------|------|
| C3-RQ1 | 总体性能 | ML / Yelp / ACM | N=50, α=1.0, C=0.2, T=100, E=5 | Hit@10, NDCG@10 |
| C3-RQ2 | 冷启动 | 三数据集 | 暖80%/冷20%，冷用户去边 | Hit@10, NDCG@10 |
| C3-RQ3 | Non-IID | ML | α∈{0.1,0.5,1.0,∞} | NDCG@10 |
| C3-ABL | 消融 | ML | w/o Attr / CL / Proto | Hit@10, NDCG@10 |

**基线**：FedNCF, FedGNN, FedPerGNN, FedHGNN, FedProto, FedASCL

### 第四章（`tab:exp_config_chap4`）

| ID | 实验 | 数据集 | 关键设定 | 输出 |
|----|------|--------|----------|------|
| C4-RQ1 | 压缩性能 | ML / Yelp / ACM | N=100, α=0.5, C=0.1, ρ=0.2, b=4 | Recall@20, NDCG@20 |
| C4-RQ2 | 消融 | ML | w/o Selector / Residual | Recall@20, NDCG@20 |
| C4-RQ3 | 通信效率 | ML | 100轮×10客户端 | MB, wall-clock |
| C4-SWEEP | ρ/b 扫描 | ML | 见 `tab:compression_tradeoff` | 多配置 |

**基线**：FedASCL-Full, Random-k, Top-k, QSGD, FedASCL-Compress

### 第五章

系统级通信仿真（REST 封装）；**排序精度引用第三章**，本复现暂不包含。

---

## 2. 分阶段实施路线

### Phase 0：基础设施（第 1 天）✅ 完成

- [x] 编写本计划书
- [x] 创建 `experiments/` 目录结构
- [x] 依赖 `requirements.txt`、配置 YAML
- [x] 指标模块 Hit@K / NDCG@K / Recall@K
- [x] Dirichlet 联邦划分
- [x] MovieLens-1M 下载与预处理脚本
- [x] `smoke_test.py` 验证环境与数据
- [x] CUDA 版 PyTorch（cu124）

### Phase 1：数据管道（第 2–3 天）✅ ML-1M 完成

- [x] MovieLens-1M：属性编码、leave-one-out 划分、BPR 负采样
- [ ] Yelp / ACM：按论文表字段预处理（可后移）
- [x] 固定 `seed=42`，保存划分到 `data/processed/`

### Phase 2：FedASCL 最小实现（第 4–10 天）✅ 核心完成

- [x] 属性 kNN 超图 + 结构二部图
- [x] 双视图编码 + InfoNCE + BPR + 原型对齐
- [x] 联邦 FedAvg + 原型聚合
- [x] MovieLens smoke 5 轮训练验证

### Phase 3：第三章实验（第 11–18 天）

- [ ] C3-RQ1 总体（6 方法 × 3 数据集 × 100 轮）
- [ ] C3-RQ2 冷启动
- [ ] C3-RQ3 Non-IID 扫描
- [ ] C3-ABL 消融
- [ ] 导出 CSV → 对比论文表 → 记录偏差

### Phase 4：基线实现（与 Phase 3 并行/交错）

- [ ] FedNCF / FedGNN（简化 GNN）/ FedProto
- [ ] FedPerGNN / FedHGNN（可引用开源或简化版）

### Phase 5：第四章压缩（第 19–24 天）

- [ ] 元路径注意力 + Top-K 剪枝
- [ ] 残差 QSGD 量化
- [ ] 通信字节统计模块
- [ ] C4 全部实验 + ρ/b 扫描

### Phase 6：验收与论文同步（第 25–28 天）

- [ ] 生成 `results/` 汇总表
- [ ] 用真实结果更新 `generate_figures.py` 或替换为真实曲线
- [ ] 答辩材料：实验 log 路径、设定对照表

---

## 3. 硬件与时间预估

| 任务 | 单次耗时（估） | 8GB GPU 可行性 |
|------|----------------|----------------|
| ML FedASCL 100轮 | 2–6 h | ✅ |
| Yelp 100轮 | 4–10 h | ⚠️ 可能 OOM，需 batch/采样 |
| ACM 100轮 | 6–12 h | ⚠️ 同上 |
| Non-IID 4×α × 4方法 | ~16–24 h | ✅（仅 ML） |
| Chap4 ρ 扫描 7 配置 | ~14–42 h | ✅（仅 ML） |

**建议**：先 **MovieLens 全链路跑通**，再扩展 Yelp/ACM。

---

## 4. 验收标准

1. **可复现**：`python scripts/run_experiment.py --config config/chap3_movielens.yaml` 一键运行并写 log
2. **有依据**：`results/` 含 CSV、config 快照、随机种子
3. **趋势一致**：FedASCL 在冷启动/强 Non-IID 上相对基线有优势（不要求数值完全一致）
4. **通信可解释**：第四章 MB 统计口径与正文一致（上传字段清单文档化）

---

## 5. 风险与对策

| 风险 | 对策 |
|------|------|
| 无历史代码 | 按 chap3 算法伪代码实现，版本记录在 git |
| 数值对不上论文 | 以真实结果为准，论文表注明「复现实验」或更新数值 |
| GPU 内存不足 | 减 embed_dim、减 batch、子图采样 |
| 基线过多 | 优先 FedGNN/FedProto/FedHGNN，FedPerGNN 可简化 |
| 周期过长 | 分 MVP（仅 ML + FedASCL + 2 基线）与 Full 两档 |

---

## 6. 目录结构（目标）

```
experiments/
├── REPRODUCTION_PLAN.md      # 本文件
├── requirements.txt
├── config/
│   ├── chap3_movielens.yaml
│   └── chap4_movielens.yaml
├── data/
│   ├── raw/                  # 原始下载（gitignore）
│   └── processed/            # 预处理后（gitignore）
├── src/
│   ├── metrics.py
│   ├── federated.py
│   ├── data/
│   └── models/               # Phase 2 起
├── scripts/
│   ├── download_movielens.py
│   ├── smoke_test.py
│   └── run_experiment.py
└── results/                  # 实验输出（gitignore）
```

---

## 7. 当前进度

- **Phase 0**：✅ 计划书 + 指标 + 联邦划分 + ML-1M 下载
- **Phase 1**：✅ 预处理脚本 `scripts/preprocess_movielens.py`，输出 `data/processed/movielens_1m.pkl`
- **Phase 2**：✅ FedASCL 模型 + 联邦训练循环（`src/models/fedascl.py`, `src/training/federated_trainer.py`）
- **CUDA PyTorch**：✅ `torch 2.6.0+cu124`，RTX 4060 可用
- **Smoke 训练**：✅ 5 轮联邦训练跑通，结果见 `results/c3_movielens_smoke_results.json`

### 快速命令

```bash
cd experiments
python scripts/preprocess_movielens.py --config config/chap3_movielens_smoke.yaml
python scripts/run_experiment.py --config config/chap3_movielens_smoke.yaml   # 5 轮 smoke
python scripts/run_experiment.py --config config/chap3_movielens.yaml           # 100 轮正式（约数小时）
python scripts/smoke_test.py
```

### 待完成

- Phase 3：100 轮正式实验 + 基线（FedGNN/FedProto 等）
- Phase 4：冷启动 / Non-IID / 消融
- Phase 5：第四章压缩实验
- Yelp / ACM 数据集
