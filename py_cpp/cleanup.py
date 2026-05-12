from __future__ import annotations

import shutil
from pathlib import Path

from .config import CONFIG
from .utils import ensure_dir


def clear_builds() -> None:
    if CONFIG.builds_dir.exists():
        shutil.rmtree(CONFIG.builds_dir, ignore_errors=True)
    ensure_dir(CONFIG.builds_dir)


def clear_cache() -> None:
    if CONFIG.cache_dir.exists():
        shutil.rmtree(CONFIG.cache_dir, ignore_errors=True)
    ensure_dir(CONFIG.cache_dir)

