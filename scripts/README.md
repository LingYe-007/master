# 论文图表生成脚本

## 依赖

```bash
pip install matplotlib
```

## 使用

在项目根目录执行：

```bash
python3 scripts/generate_figures.py
```

会在 `images/` 下生成：

| 文件 | 对应章节 | 说明 |
|------|----------|------|
| `ablation_study.png` | 第四章 4.4 | 消融实验：Full / w/o Selector / w/o Residual 的 Recall@20、NDCG@20 柱状图 |
| `denoising_curve.png` | 第四章 4.5 | 元路径保留率 ρ 与 Recall@20 曲线（先升后降，峰值约 ρ=0.5） |
| `pareto_efficiency.png` | 第四章 4.6 | 通信量–精度帕累托图，FedASCL-Compress 位于左上角 |
| `system_architecture.png` | 第五章 5.2 | 系统四层总体架构图 |

如需修改数据或样式，请编辑 `generate_figures.py` 中对应函数。
