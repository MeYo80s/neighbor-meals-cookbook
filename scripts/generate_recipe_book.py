#!/usr/bin/env python3
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "RECIPE_BOOK.md"
INDEX = ROOT / "RECIPE_INDEX.md"
DROP_OFF = ROOT / "docs" / "drop-off-options.md"
TRANSPORT = ROOT / "docs" / "simple-transport-meals.md"
SITE = ROOT / "docs" / "index.html"
NOJEKYLL = ROOT / "docs" / ".nojekyll"


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


def inline_md_to_html(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def markdown_to_html(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    in_ul = False
    in_ol = False

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            close_lists()
            continue

        if stripped.startswith("# "):
            close_lists()
            heading_text = stripped[2:].strip()
            out.append(f"<h1 id=\"{slugify(heading_text)}\">{inline_md_to_html(heading_text)}</h1>")
            continue
        if stripped.startswith("## "):
            close_lists()
            heading_text = stripped[3:].strip()
            out.append(f"<h2 id=\"{slugify(heading_text)}\">{inline_md_to_html(heading_text)}</h2>")
            continue
        if stripped.startswith("### "):
            close_lists()
            heading_text = stripped[4:].strip()
            out.append(f"<h3 id=\"{slugify(heading_text)}\">{inline_md_to_html(heading_text)}</h3>")
            continue

        if re.match(r"^\d+\.\s+", stripped):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            content = re.sub(r"^\d+\.\s+", "", stripped)
            out.append(f"<li>{inline_md_to_html(content)}</li>")
            continue

        if stripped.startswith("- "):
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline_md_to_html(stripped[2:].strip())}</li>")
            continue

        if stripped == "---":
            close_lists()
            out.append("<hr>")
            continue

        close_lists()
        out.append(f"<p>{inline_md_to_html(stripped)}</p>")

    close_lists()
    return "\n".join(out)


def write_site_html(markdown_text: str) -> None:
    body = markdown_to_html(markdown_text)
    html_text = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>Neighbor Meals Cookbook</title>
  <style>
    :root {{
      --bg: #f8f5ee;
      --surface: #fffdf9;
      --ink: #2c2a26;
      --accent: #8f3f2a;
      --line: #e5ddd0;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background: radial-gradient(circle at top right, #f2eadc, var(--bg));
      line-height: 1.55;
    }}
    main {{
      max-width: 920px;
      margin: 2rem auto;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 2rem;
      box-shadow: 0 10px 25px rgba(0,0,0,.06);
    }}
    h1, h2, h3 {{ line-height: 1.2; }}
    h1 {{ margin-top: 0; font-size: 2rem; color: var(--accent); }}
    h2 {{ margin-top: 2rem; color: var(--accent); border-top: 1px solid var(--line); padding-top: 1rem; }}
    h3 {{ margin-top: 1.25rem; }}
    p, li {{ font-size: 1rem; }}
    ul, ol {{ padding-left: 1.25rem; }}
    hr {{ border: 0; border-top: 1px solid var(--line); margin: 1.5rem 0; }}
    code {{ background: #f3ede2; padding: .1rem .3rem; border-radius: 4px; }}
    a {{ color: var(--accent); }}
    .meta {{ font-size: .95rem; color: #5f5546; margin-bottom: 1rem; }}
    @media (max-width: 768px) {{
      main {{ margin: 1rem; padding: 1.25rem; }}
      h1 {{ font-size: 1.6rem; }}
    }}
  </style>
</head>
<body>
  <main>
    <div class=\"meta\">Neighbor Meals Ward Cookbook</div>
    {body}
  </main>
</body>
</html>
"""
    SITE.write_text(html_text, encoding="utf-8")
    NOJEKYLL.write_text("\n", encoding="utf-8")


def main() -> None:
    idx = INDEX.read_text(encoding="utf-8")
    sections = parse_index_sections(idx)
    section_recipes: list[tuple[str, list[tuple[int, str, str]]]] = []
    toc_sections: list[tuple[str, list[tuple[int, str]]]] = []
    counter = 1

    for section in sections:
        section_title = str(section["title"])
        section_entries: list[tuple[int, str]] = []
        section_recipe_entries: list[tuple[int, str, str]] = []
        for path in section["paths"]:
            if not path.exists():
                continue
            title, body = read_recipe(path)
            section_entries.append((counter, title))
            section_recipe_entries.append((counter, title, body))
            counter += 1
        toc_sections.append((section_title, section_entries))
        section_recipes.append((section_title, section_recipe_entries))

    lines: list[str] = [
        "# Neighbor Meals Cookbook",
        "",
        "A collection of simple, comforting meals designed for sharing with neighbors and friends during times of need.",
        "",
        "## Table of Contents",
        "- [How to Use This Book](#how-to-use-this-book)",
    ]

    for section_title, section_entries in toc_sections:
        lines.append(f"- [{section_title}](#{slugify(section_title)})")
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
        "- Run `python3 scripts/generate_recipe_book.py` to rebuild this book and website.",
        "",
        "---",
    ])

    for section_title, recipe_entries in section_recipes:
        lines.extend([
            "",
            f"## {section_title}",
        ])
        if not recipe_entries:
            lines.extend([
                "",
                "_Coming soon_",
                "",
                "---",
            ])
            continue
        for number, title, body in recipe_entries:
            lines.extend([
                "",
                f"### {number}) {title}",
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

    markdown_text = "\n".join(lines).rstrip() + "\n"
    BOOK.write_text(markdown_text, encoding="utf-8")
    write_site_html(markdown_text)


if __name__ == "__main__":
    main()
