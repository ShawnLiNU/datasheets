#!/usr/bin/env python3
"""Rebuild the datasheet list in README.md from the PDFs in docs/."""

from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
README = ROOT / "README.md"
START = "<!-- DATASHEETS:START -->"
END = "<!-- DATASHEETS:END -->"
EXTENSIONS = {".pdf"}  # add ".stp" here to also list CAD files


def sort_key(path):
    return path.as_posix().casefold()


def link(path, base):
    label = path.relative_to(base).as_posix().replace("[", "\\[").replace("]", "\\]")
    target = quote(path.relative_to(ROOT).as_posix())
    return f"[{label}]({target})"


def build_list():
    loose, groups = [], {}
    for path in DOCS.rglob("*"):
        parts = path.relative_to(DOCS).parts
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        if any(part.startswith(".") for part in parts):
            continue
        if len(parts) == 1:
            loose.append(path)
        else:
            groups.setdefault(parts[0], []).append(path)

    lines = [f"- {link(p, DOCS)}" for p in sorted(loose, key=sort_key)]
    for group in sorted(groups, key=str.casefold):
        lines.append(f"- {group}")
        for p in sorted(groups[group], key=sort_key):
            lines.append(f"  - {link(p, DOCS / group)}")
    return "\n".join(lines) if lines else "_No datasheets yet._"


def main():
    text = README.read_text(encoding="utf-8")
    block = f"{START}\n{build_list()}\n{END}"

    if START in text and END in text:
        before = text.partition(START)[0]
        after = text.partition(END)[2]
        new_text = before + block + after
    else:
        new_text = text.rstrip() + "\n\n## Current hardware\n\n" + block + "\n"

    if new_text != text:
        README.write_text(new_text, encoding="utf-8")
        print("README.md updated")
    else:
        print("README.md already up to date")


if __name__ == "__main__":
    main()
