#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Build the Aizen web kit: one self-contained Markdown file a chat AI can follow without the skill installed.

    uv run export_web.py --out docs/aizen-web-kit.md      # write the kit
    uv run export_web.py --check docs/aizen-web-kit.md    # exit 1 when the committed kit is stale
    uv run export_web.py                                  # print to stdout
    uv run export_web.py --selfcheck

The kit = assets/prompt/web-kit-head.md + the skill's Workflow + references/prompt/interview.md +
references/prompt/format.md, with file references rewritten to section names ("Interview §2", "Prompt §4").
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
PARTS = (("Interview", "references/prompt/interview.md"), ("Prompt", "references/prompt/format.md"))


def read(rel: str) -> str:
    return (SKILL / rel).read_text(encoding="utf-8").replace("\r\n", "\n")


def section(text: str, title: str) -> str:
    """Body of the `## <title>` section, without its heading."""
    m = re.search(rf"^## {re.escape(title)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        raise SystemExit(f"export_web: SKILL.md has no '## {title}' section")
    return m.group(1).strip()


def localise(text: str) -> str:
    """File references → section names the chat AI can find in the kit."""
    for name, rel in PARTS:
        text = re.sub(rf"`{re.escape(rel)}`\s*§", f"{name} §", text)
        text = text.replace(f"`{rel}`", name)
    text = re.sub(r"Inside a project with `\.aizen/`:.*?In a web chat: the ", "The ", text, flags=re.S)
    return text


def demote(text: str) -> str:
    """Shift headings one level down under the kit's own `##` parts; drop the file's `#` title."""
    out = []
    for line in text.split("\n"):
        if line.startswith("# "):
            continue
        out.append("#" + line if re.match(r"#{2,5} ", line) else line)
    return "\n".join(out).strip()


def build() -> str:
    skill = read("SKILL.md")
    parts = [read("assets/prompt/web-kit-head.md").strip(),
             "## Workflow\n\n" + localise(section(skill, "Workflow")),
             "## Gotchas\n\n" + localise(section(skill, "Gotchas"))]
    for name, rel in PARTS:
        parts.append(f"## {name}\n\n" + localise(demote(read(rel))))
    kit = "\n\n".join(parts) + "\n"
    left = re.findall(r"`(?:references|assets|scripts)/[^`]+`", kit)
    if left:
        raise SystemExit(f"export_web: file references left in the kit: {sorted(set(left))}")
    return kit


def selfcheck() -> int:
    kit = build()
    assert kit.startswith("# Aizen web kit"), kit[:40]
    for must in ("## Workflow", "## Interview", "## Prompt", "### 2. Shape", "Tên nghiệp vụ", "Interview §2", "Prompt §4"):
        assert must in kit, must
    assert "references/prompt" not in kit and "SKILL_DIR" not in kit
    assert "**Deliver.** The code block is the delivery" in kit
    assert "\n# " not in kit[2:], "only the kit title may be a level-1 heading"
    print("export_web self-check: OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the Aizen web kit for chat AIs")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--out", help="write the kit to this file")
    g.add_argument("--check", metavar="FILE", help="exit 1 when FILE differs from a fresh build")
    g.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()
    if a.selfcheck:
        return selfcheck()
    kit = build()
    if a.check:
        p = Path(a.check)
        if not p.is_file() or p.read_text(encoding="utf-8").replace("\r\n", "\n") != kit:
            print(f"✗ {p} is stale — run: uv run export_web.py --out {p}", file=sys.stderr)
            return 1
        print(f"✓ {p} is up to date")
        return 0
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(kit, encoding="utf-8", newline="\n")
        print(f"✓ web kit → {a.out} ({len(kit.splitlines())} lines)")
        return 0
    sys.stdout.write(kit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
