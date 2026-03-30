"""Keep only \\cite'd entries in chapters/reference.bib (master thesis: 参考文献与正文一致)."""
import re
import pathlib


def split_bib_entries(text: str) -> list[str]:
    entries, i, n = [], 0, len(text)
    while i < n:
        if text[i] == "@":
            start = i
            i += 1
            while i < n and text[i] != "{":
                i += 1
            if i >= n:
                break
            i += 1
            depth = 1
            while i < n and depth:
                if text[i] == "{":
                    depth += 1
                elif text[i] == "}":
                    depth -= 1
                i += 1
            entries.append(text[start:i].strip())
        else:
            i += 1
    return entries


def entry_key(block: str) -> str | None:
    m = re.match(r"@\w+\{([^,]+),", block)
    return m.group(1).strip() if m else None


def main() -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    tex = (root / "main.tex").read_text(encoding="utf-8")
    for p in (root / "chapters").glob("*.tex"):
        tex += p.read_text(encoding="utf-8", errors="ignore")
    cite_pat = re.compile(r"\\cite[a-zA-Z]*(?:\[[^\]]*\])?\{([^}]+)\}")
    cited: set[str] = set()
    for m in cite_pat.finditer(tex):
        cited.update(x.strip() for x in m.group(1).split(","))

    bib_path = root / "chapters" / "reference.bib"
    raw = bib_path.read_text(encoding="utf-8")
    blocks = split_bib_entries(raw)
    keys_in_bib = {entry_key(b) for b in blocks}
    keys_in_bib.discard(None)
    kept = [b for b in blocks if entry_key(b) in cited]
    missing = sorted(cited - keys_in_bib)
    if missing:
        raise SystemExit(f"Cited keys missing from bib: {missing}")
    bib_path.write_text("\n\n".join(kept) + "\n", encoding="utf-8")
    print(f"Kept {len(kept)} entries; removed {len(blocks) - len(kept)}")


if __name__ == "__main__":
    main()
