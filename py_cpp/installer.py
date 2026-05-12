from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from .config import CONFIG
from .dependency_manager import vcpkg_triplet_for_current_platform
from .errors import PyCppError, VcpkgError
from .logging_utils import get_logger
from .metadata import PackageMetadata, load_packages_metadata, save_packages_metadata
from .platform_utils import which
from .utils import ensure_dir, run

log = get_logger(__name__)


@dataclass(frozen=True)
class VcpkgInfo:
    root: Path
    exe: Path


def find_vcpkg() -> VcpkgInfo | None:
    root_env = os.environ.get("VCPKG_ROOT")
    if root_env:
        exe = Path(root_env) / ("vcpkg.exe" if os.name == "nt" else "vcpkg")
        if exe.exists():
            return VcpkgInfo(root=Path(root_env), exe=exe)

    exe_path = which("vcpkg.exe" if os.name == "nt" else "vcpkg")
    if exe_path:
        exe = Path(exe_path)
        # vcpkg is typically in <root>/vcpkg(.exe)
        return VcpkgInfo(root=exe.parent, exe=exe)

    managed_root = Path(CONFIG.home_dir) / "vcpkg"
    managed_exe = managed_root / ("vcpkg.exe" if os.name == "nt" else "vcpkg")
    if managed_exe.exists():
        return VcpkgInfo(root=managed_root, exe=managed_exe)

    return None


def bootstrap_vcpkg() -> VcpkgInfo:
    if which("git") is None:
        raise VcpkgError("Git is required to bootstrap vcpkg automatically. Install Git or set VCPKG_ROOT.")

    root = ensure_dir(Path(CONFIG.home_dir) / "vcpkg")
    exe = root / ("vcpkg.exe" if os.name == "nt" else "vcpkg")
    if exe.exists():
        return VcpkgInfo(root=root, exe=exe)

    # Clean non-empty directory to avoid broken bootstrap states.
    if any(root.iterdir()):
        shutil.rmtree(root, ignore_errors=True)
        ensure_dir(root)

    run(["git", "clone", "https://github.com/microsoft/vcpkg.git", str(root)])

    if os.name == "nt":
        run([str(root / "bootstrap-vcpkg.bat")], cwd=root)
    else:
        run(["sh", str(root / "bootstrap-vcpkg.sh")], cwd=root)

    if not exe.exists():
        raise VcpkgError("vcpkg bootstrap completed but vcpkg executable was not found.")
    return VcpkgInfo(root=root, exe=exe)


def install(package: str, *, triplet: str | None = None) -> bool:
    """
    Install a vcpkg port and persist metadata for later builds.
    """
    info = find_vcpkg() or bootstrap_vcpkg()
    use_triplet = triplet or vcpkg_triplet_for_current_platform()

    try:
        run([str(info.exe), "install", package, "--triplet", use_triplet], cwd=info.root)
    except PyCppError:
        print("Sorry, library not found.")
        return False

    meta = load_packages_metadata()
    packages = list(meta.packages)
    packages.append(package)
    save_packages_metadata(
        PackageMetadata(vcpkg_root=str(info.root), triplet=use_triplet, packages=packages)
    )
    return True


def get_vcpkg_root_and_triplet() -> tuple[Path, str] | None:
    meta = load_packages_metadata()
    if not meta.vcpkg_root or not meta.triplet:
        return None
    root = Path(meta.vcpkg_root)
    if not root.exists():
        return None
    return root, meta.triplet

