# 参考文献显示为 key（如 luo2024perfedrec）而非数字标号的原因与解决

## 一、原因分析

正文引用显示为**文献 key**（如 `luo2024perfedrec`、`wu2021fedgnn`）而不是**数字上标**（如 ¹、²、³），是因为 **biblatex 没有读到由 biber 生成的 .bbl 文件**。

具体机制如下：

1. 使用 **`xelatex -output-directory=output main.tex`** 时，`main.aux`、`main.bcf` 等辅助文件会写在 **`output/`** 目录下。
2. **biblatex** 在第二次及以后的 xelatex 运行中，会到 **与 .aux 同一目录**（即 `output/`）下去找 **`main.bbl`**。
3. **`main.bbl`** 必须由 **biber** 根据 `main.bcf` 和 `chapters/reference.bib` 生成。若从未成功生成，或生成到了别的位置，则 `output/main.bbl` 不存在。
4. 在您当前的 `output/main.aux` 中有：
   - `\abx@aux@read@bbl@mdfivesum{nobblfile}`
   - `\abx@aux@read@bblrerun`  
   说明 biblatex 认为「没有 .bbl 文件」，因此无法分配数字编号，只能退化为显示 **cite key**。

常见导致「没有 .bbl」的情况：

- **没有运行 biber**，或只跑了 xelatex。
- **biber 的调用方式不对**：例如在项目根目录执行 `biber main`。此时 biber 会在当前目录找 `main.bcf`，而实际 `main.bcf` 在 `output/main.bcf`，所以要么报错，要么在错误位置生成/不生成 `main.bbl`，`output/` 下仍然没有 `main.bbl`。
- **输出目录不一致**：若用其他方式（如 IDE）编译且输出目录不是 `output/`，则要保证 biber 和 xelatex 使用**同一输出目录**。

结论：**引用显示为 key 的直接原因是：在用于本次编译的 output 目录下，没有正确生成或未被使用到 `main.bbl`。**

---

## 二、正确操作步骤（在项目根目录执行）

在**包含 `main.tex` 的项目根目录**下，按顺序执行：

```bash
# 1. 第一遍 xelatex（生成 .aux、.bcf）
xelatex -output-directory=output -interaction=nonstopmode main.tex

# 2. 运行 biber，注意参数是 output/main（不是 main）
biber output/main

# 3. 第二遍 xelatex（读入 .bbl，写出引用编号）
xelatex -output-directory=output -interaction=nonstopmode main.tex

# 4. 第三遍 xelatex（稳定交叉引用与参考文献列表）
xelatex -output-directory=output -interaction=nonstopmode main.tex
```

要点：

- **必须执行第 2 步**，且命令是 **`biber output/main`**，这样 biber 才会：
  - 读 `output/main.bcf`
  - 读 `chapters/reference.bib`（路径相对项目根目录）
  - 写 **`output/main.bbl`**
- 第 3、4 步中，xelatex 会从 `output/` 读入 `main.bbl`，正文中的 `\cite{...}` 才会变成数字上标，文末参考文献表也会正常生成。

若使用 **TeXstudio / VS Code / Cursor** 等：

- 若编译器设置为「输出到 `output` 目录」，则对应的 **Biber 命令也要指向该目录**（例如 `biber output/main` 或工具里配置的等价命令），保证生成的 `main.bbl` 在 `output/` 下。
- 编译顺序保持：**xelatex → biber → xelatex → xelatex**。

---

## 三、如何确认已修复

- 打开 **`output/main.bbl`**，应能看到类似 `\abx@entry`、`\abx@list` 等 biblatex 的条目，且为可读文本（无乱码）。
- 再运行两遍 xelatex 后，打开 **`output/main.pdf`**：
  - 正文中的引用应为**上标数字**（如 ¹、²、³），而不是 `luo2024perfedrec` 等 key。
  - 文末「参考文献」列表应按顺序列出所有被引文献。

若按上述步骤操作后仍显示为 key，请检查：

1. 是否在**项目根目录**下执行，且 biber 命令为 **`biber output/main`**。
2. 是否存在 **`output/main.bbl`**，且未被其他工具覆盖或损坏。
3. 修改过 `reference.bib` 或引用后，是否重新执行了 **biber → xelatex → xelatex**。
