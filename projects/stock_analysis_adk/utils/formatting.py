from __future__ import annotations

import json
from typing import Any


def safe_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def compact_float(value: Any, ndigits: int = 2) -> Any:
    try:
        return round(float(value), ndigits)
    except Exception:
        return value


def dict_to_bullets(d: dict, indent: int = 0) -> str:
    pad = "  " * indent
    lines = []
    for k, v in d.items():
        if isinstance(v, dict):
            lines.append(f"{pad}- **{k}**:")
            lines.append(dict_to_bullets(v, indent + 1))
        else:
            lines.append(f"{pad}- **{k}**: {v}")
    return "\n".join(lines)
