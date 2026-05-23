# thesis-to-ppt — 参考与示例

## Marp 最小骨架（选项 A）

用户在文件首行可使用（按本机 Marp 插件要求调整）：

```markdown
---
marp: true
theme: default
paginate: true
---

# 论文题目
**答辩人**：XXX ｜ **导师**：XXX ｜ **日期**：YYYY-MM-DD

---

# 目录
- 研究背景与意义
- 国内外研究现状
- …
```

分页用单独一行的 `---`。

## 图占位写法

```markdown
# FedASCL 总体框架
<!-- 口播：双视图 + 原型 + 联邦闭环，约 45 秒 -->

![w:800](占位：从 PDF 截取 `fedascl_framework.png`)
```

## 实验页写法（与正文表号一致）

```markdown
# 实验：总体性能（RQ1）
- 数据集：MovieLens-1M / Yelp / ACM
- 对比：FedNCF … FedProto（见论文表 `tab:overall_performance`）
- 结论：**一句与正文一致**，不新造数字
```

## 备用页（可选）

- **创新点**：三条，与第一章贡献节动词对齐。
- **局限**：硬阈值剪枝、原型加权、未并列 ACM 压缩数——各**一句**，与第四章小结/对照文档一致。
