from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import CONFIG
from .utils import ensure_dir
import importlib.resources as resources


@dataclass(frozen=True)
class PackageMetadata:
    vcpkg_root: str | None
    triplet: str | None
    packages: list[str]


def metadata_path() -> Path:
    ensure_dir(CONFIG.home_dir)
    return CONFIG.home_dir / CONFIG.vcpkg_meta_name


def load_packages_metadata() -> PackageMetadata:
    p = metadata_path()
    if not p.exists():
        # Seed from packaged default if available
        try:
            default_text = resources.files("py_cpp.data").joinpath("packages.json").read_text(encoding="utf-8")
            p.write_text(default_text, encoding="utf-8")
        except Exception:
            return PackageMetadata(vcpkg_root=None, triplet=None, packages=[])
    raw: dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
    return PackageMetadata(
        vcpkg_root=raw.get("vcpkg_root"),
        triplet=raw.get("triplet"),
        packages=list(raw.get("packages") or []),
    )


def save_packages_metadata(meta: PackageMetadata) -> None:
    p = metadata_path()
    p.write_text(
        json.dumps(
            {
                "vcpkg_root": meta.vcpkg_root,
                "triplet": meta.triplet,
                "packages": sorted(set(meta.packages)),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
