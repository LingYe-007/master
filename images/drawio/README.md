# 论文图片 Draw.io 源文件

本目录包含论文中各概念图、流程图的 Draw.io 源文件，可在 [Draw.io](https://app.diagrams.net/) 或 VS Code 的 Draw.io 插件中打开编辑。

## 文件列表与对应图片

| 文件名 | 对应论文图片 | 章节 |
|--------|--------------|------|
| 01_论文结构.drawio | 论文结构.png | 第一章 |
| 02_压缩流程示意图.drawio | 压缩流程示意图.png | 第四章 |
| 03_二部图与矩阵.drawio | bipartite_matrix.png | 第二章 |
| 04_同构图与异构图对比.drawio | 同构图与异构图对比.png | 第二章 |
| 05_元路径.drawio | 元路径.png | 第二章 |
| 06_动态元路径选择器.drawio | selector_logic.png | 第四章 |
| 07_系统架构.drawio | system_architecture_cn.png | 第五章 |
| 08_跨视图对比机制.drawio | 跨视图对比机制 | 第三章 |
| 09_基于原型的语义对齐.drawio | 基于原型的语义对齐策略.png | 第三章 |
| 10_图神经网络.drawio | 图神经网络.png | 第二章 |
| 11_属性语义图构建.drawio | 属性语义图构建.png | 第三章 |
| 12_超图对比.drawio | hypergraph_compare | 第二章 |
| 13_联邦学习架构.drawio | 联邦学习.png | 第二章 |
| 14_冷启动推荐策略.drawio | 冷启动推荐策略流程图.png | 第五章 |
| 15_横向纵向联邦对比.drawio | horizontal_vertical_fl | 第二章 |
| 16_联邦原型对齐.drawio | fed_prototype_align | 第二章 |

## 使用方法

1. 用 Draw.io 打开：访问 https://app.diagrams.net/ ，选择「打开已有图表」→ 选择对应 .drawio 文件
2. 编辑后导出：文件 → 导出为 → PNG/PDF/SVG
3. 将导出图片放到 `images/` 目录，替换原对应图片

## 文字格式规范

参见 [文字格式规范.md](./文字格式规范.md)，包含字号、配色、绘制建议等。

## 重新生成

运行 `python scripts/generate_drawio.py` 可重新生成所有 Draw.io 文件（会覆盖当前文件）。
