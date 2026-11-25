"""Pure G-code tool remapping. No OrcaSlicer imports, so it is testable anywhere."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path

_TOOL_CHANGE = re.compile(r"^(\s*)T(\d+)\b")
# Temperature commands that address a specific tool via a T parameter.
_TOOL_PARAM_CMD = re.compile(r"^\s*M(?:104|109|568)\b", re.IGNORECASE)
_TOOL_PARAM = re.compile(r"(\s)T(\d+)\b")


def parse_mapping(raw: Mapping[str, int] | Mapping[int, int], toolhead_count: int) -> dict[int, int]:
    """Validate a {filament_index: toolhead_index} mapping read from the plugin config.

    Raises ValueError for out-of-range indices or two filaments on the same toolhead.
    """
    mapping: dict[int, int] = {}
    for key, value in raw.items():
        src, dst = int(key), int(value)
        if src < 0:
            raise ValueError(f"filament index {src} is negative")
        if not 0 <= dst < toolhead_count:
            raise ValueError(f"toolhead {dst} for filament {src} is outside 0..{toolhead_count - 1}")
        mapping[src] = dst

    targets = list(mapping.values())
    if len(targets) != len(set(targets)):
        raise ValueError("two filaments are mapped to the same toolhead")
    return mapping


def is_identity(mapping: Mapping[int, int]) -> bool:
    return all(src == dst for src, dst in mapping.items())


def remap_line(line: str, mapping: Mapping[int, int]) -> str:
    """Remap tool numbers in one G-code line, leaving comments untouched."""
    code, sep, comment = line.partition(";")

    def sub(match: re.Match[str]) -> str:
        tool = int(match.group(2))
        return f"{match.group(1)}T{mapping.get(tool, tool)}"

    if _TOOL_CHANGE.match(code):
        code = _TOOL_CHANGE.sub(sub, code, count=1)
    elif _TOOL_PARAM_CMD.match(code):
        code = _TOOL_PARAM.sub(sub, code, count=1)
    return code + sep + comment


def remap_file(path: str | Path, mapping: Mapping[int, int]) -> int:
    """Rewrite the G-code file in place. Returns the number of changed lines."""
    path = Path(path)
    # newline="" keeps the file's original line endings.
    with path.open("r", encoding="utf-8", newline="") as f:
        lines = f.readlines()

    changed = 0
    out = []
    for line in lines:
        new = remap_line(line, mapping)
        changed += new != line
        out.append(new)

    if changed:
        with path.open("w", encoding="utf-8", newline="") as f:
            f.writelines(out)
    return changed
