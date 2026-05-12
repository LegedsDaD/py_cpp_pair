from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


def _default_home_dir() -> Path:
    override = os.environ.get("PY_CPP_HOME")
    if override:
        return Path(override)

    if sys.platform.startswith("win"):
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or str(Path.home())
        return Path(base) / "py_cpp"

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "py_cpp"

    # linux + other unix
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / "py_cpp"
    return Path.home() / ".local" / "share" / "py_cpp"


@dataclass(frozen=True)
class Config:
    home_dir: Path = _default_home_dir()
    cache_dir_name: str = "cache"
    builds_dir_name: str = "builds"
    logs_dir_name: str = "logs"
    vcpkg_meta_name: str = "packages.json"

    @property
    def cache_dir(self) -> Path:
        return self.home_dir / self.cache_dir_name

    @property
    def builds_dir(self) -> Path:
        return self.home_dir / self.builds_dir_name

    @property
    def logs_dir(self) -> Path:
        return self.home_dir / self.logs_dir_name


CONFIG = Config()
