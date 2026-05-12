from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .config import CONFIG
from .utils import ensure_dir


@dataclass(frozen=True)
class CacheEntry:
    key: str
    build_dir: Path
    module_name: str
    pyd_path: Path
    meta_path: Path


def cache_root() -> Path:
    return ensure_dir(CONFIG.cache_dir)


def compute_key(code: str) -> str:
    h = hashlib.sha256()
    h.update(code.encode("utf-8"))
    return h.hexdigest()


def get_entry(code: str) -> CacheEntry:
    key = compute_key(code)
    build_dir = ensure_dir(CONFIG.builds_dir / key)
    module_name = f"pycpp_{key[:12]}"
    # Real extension suffix depends on platform/python build
    from .utils import get_ext_suffix

    pyd_path = build_dir / f"{module_name}{get_ext_suffix()}"
    meta_path = build_dir / "build_meta.json"
    return CacheEntry(key=key, build_dir=build_dir, module_name=module_name, pyd_path=pyd_path, meta_path=meta_path)


def load_meta(entry: CacheEntry) -> dict:
    if not entry.meta_path.exists():
        return {}
    return json.loads(entry.meta_path.read_text(encoding="utf-8"))


def save_meta(entry: CacheEntry, meta: dict) -> None:
    entry.meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
