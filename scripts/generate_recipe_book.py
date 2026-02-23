#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "RECIPE_BOOK.md"
INDEX = ROOT / "RECIPE_INDEX.md"
DROP_OFF = ROOT / "docs" / "drop-off-options.md"
TRANSPORT = ROOT / "docs" / "simple-transport-meals.md"


def slugify(text: str) -> str:
    text = text.lower()
    text = text.replace("'", "").replace("’", "")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def parse_index_sections(index_text: str) -> list[dict[str, list[Path] | str]]:
    sections: list[dict[str, list[Path] | str]] = []
    current: dict[str, list[Path] | str] | None = None
    for line in index_text.splitlines():
        if line.startswith("## "):
            current = {"title": line[3:].strip(), "paths": []}
            sections.append(current)
            continue
        m = re.search(r"\((recipes/[^)]+\.md)\)", line)
        if m and current is not None:
            current["paths"].append(ROOT / m.group(1))
    return sections


def read_recipe(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8").strip()
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError(f"Missing title heading in {path}")
    title = lines[0][2:].strip()
    body = "\n".join(lines[1:]).strip()
    return title, body


def read_doc_without_h1(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join(lines[1:]).strip()
    return text


def main() -> None:
    idx = INDEX.read_text(encoding="utf-8")
    sections = parse_index_sections(idx)
    recipes: list[tuple[str, str]] = []
    toc_sections: list[tuple[str, list[tuple[int, str]]]] = []
    counter = 1

    for section in sections:
        section_title = str(section["title"])
        section_entries: list[tuple[int, str]] = []
        for path in section["paths"]:
            if not path.exists():
                continue
            title, body = read_recipe(path)
            recipes.append((title, body))
            section_entries.append((counter, title))
            counter += 1
        toc_sections.append((section_title, section_entries))

    lines: list[str] = [
        "# Neighbor Meals Cookbook",
        "",
        "A collection of simple, comforting meals designed for sharing with neighbors and friends during times of need.",
        "",
        "## Table of Contents",
        "- [How to Use This Book](#how-to-use-this-book)",
    ]

    for section_title, section_entries in toc_sections:
        lines.append(f"- **{section_title}**")
        if section_entries:
            for number, title in section_entries:
                lines.append(f"  - [{number}) {title}](#{number}-{slugify(title)})")
        else:
            lines.append("  - _Coming soon_")

    lines.extend([
        "- [Ready-to-Purchase Drop-Off Options](#ready-to-purchase-drop-off-options)",
        "- [Homemade Meals That Travel Well (Simple)](#homemade-meals-that-travel-well-simple)",
        "- [Helpful Delivery Notes](#helpful-delivery-notes)",
        "",
        "## How to Use This Book",
        "- Add or edit recipes in `recipes/`.",
        "- Keep `RECIPE_INDEX.md` updated with links to each recipe.",
        "- Run `python3 scripts/auto_nutrition.py` to auto-add estimated calories/macros.",
        "- Run `python3 scripts/generate_recipe_book.py` to rebuild this book.",
        "",
        "---",
    ])

    for i, (title, body) in enumerate(recipes, start=1):
        lines.extend([
            "",
            f"## {i}) {title}",
            body,
            "",
            "---",
        ])

    lines.extend([
        "",
        "## Ready-to-Purchase Drop-Off Options",
        read_doc_without_h1(DROP_OFF),
        "",
        "---",
        "",
        "## Homemade Meals That Travel Well (Simple)",
        read_doc_without_h1(TRANSPORT),
        "",
        "---",
        "",
        "## Helpful Delivery Notes",
        "- Label each meal with reheating instructions.",
        "- Include allergen notes (dairy, gluten, nuts).",
        "- Use disposable pans when possible to avoid return logistics.",
        "- Add a simple note of encouragement.",
        "- If appropriate, bring a complete meal: main dish, side, and simple dessert.",
    ])

    BOOK.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
