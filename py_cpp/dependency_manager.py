from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .logging_utils import get_logger
from .metadata import load_packages_metadata
from .platform_utils import get_platform_info

log = get_logger(__name__)


@dataclass(frozen=True)
class DepFlags:
    include_dirs: list[Path]
    library_dirs: list[Path]
    libraries: list[str]
    bin_dirs: list[Path]
    extra_link_args: list[str]


def vcpkg_triplet_for_current_platform() -> str:
    p = get_platform_info()
    machine = p.machine.lower()
    is_arm = "arm" in machine
    if p.is_windows:
        return "x64-mingw-dynamic"
    if p.is_linux:
        return "arm64-linux" if is_arm else "x64-linux"
    if p.is_macos:
        return "arm64-osx" if is_arm else "x64-osx"
    return "x64-linux"


def get_vcpkg_flags() -> DepFlags:
    meta = load_packages_metadata()
    if not meta.vcpkg_root or not meta.triplet:
        return DepFlags([], [], [], [], [])

    root = Path(meta.vcpkg_root)
    installed = root / "installed" / meta.triplet
    include_dir = installed / "include"
    lib_dir = installed / "lib"
    bin_dir = installed / "bin"

    include_dirs = [include_dir] if include_dir.exists() else []
    library_dirs = [lib_dir] if lib_dir.exists() else []
    bin_dirs = [bin_dir] if bin_dir.exists() else []

    libraries: list[str] = []
    if lib_dir.exists():
        for pkg in meta.packages:
            if (lib_dir / f"lib{pkg}.a").exists() or (lib_dir / f"lib{pkg}.so").exists() or (lib_dir / f"lib{pkg}.dylib").exists():
                libraries.append(pkg)
            elif (lib_dir / f"{pkg}.lib").exists():
                libraries.append(pkg)

    return DepFlags(include_dirs, library_dirs, libraries, bin_dirs, extra_link_args=[])

