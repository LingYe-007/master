#!/usr/bin/env python3
"""Remove \\textbf{...} from thesis chapter .tex files; keep inner if it contains
\\mathbf or \\boldsymbol. Uses balanced-brace parsing for nested \\text{...} etc."""
from __future__ import annotations

import sys
from pathlib import Path

FILES = [
    "chapters/chap1_intro.tex",
    "chapters/chap2_related.tex",
    "chapters/chap3_method.tex",
    "chapters/chap4_compression.tex",
    "chapters/chap5_system.tex",
    "chapters/chap6_summary.tex",
    "backmatter/resume.tex",
]

PREFIX = r"\textbf{"


def strip_textbf(s: str) -> str:
    result: list[str] = []
    i, n = 0, len(s)
    while i < n:
        if s.startswith(PREFIX, i):
            j = i + len(PREFIX)
            depth, start = 1, j
            while j < n and depth:
                c = s[j]
                if c == "{":
                    depth += 1
                elif c == "}":
                    depth -= 1
                j += 1
            inner = s[start : j - 1]
            if "\\mathbf" in inner or "\\boldsymbol" in inner:
                result.append(s[i:j])
            else:
                result.append(inner)
            i = j
        else:
            result.append(s[i])
            i += 1
    return "".join(result)


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    for rel in FILES:
        p = root / rel
        if not p.is_file():
            print("skip missing", rel, file=sys.stderr)
            continue
        old = p.read_text(encoding="utf-8")
        new = strip_textbf(old)
        if new != old:
            p.write_text(new, encoding="utf-8")
            print("updated", rel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
