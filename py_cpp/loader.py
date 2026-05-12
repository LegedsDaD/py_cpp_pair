from __future__ import annotations

import importlib.util
import os
import shutil
import sys
from pathlib import Path
from types import ModuleType

from .utils import PyCppError
from .dependency_manager import get_vcpkg_flags


def load_extension_module(*, module_name: str, pyd_path: Path) -> ModuleType:
    if not pyd_path.exists():
        raise PyCppError(f"Compiled module not found: {pyd_path}")

    # Help Windows locate dependent DLLs (libstdc++/libgcc, vcpkg bins, python DLL, etc.)
    _add_dll_search_dirs(pyd_path)

    # Avoid name collisions: use unique module_name per hash.
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, str(pyd_path))
    if spec is None or spec.loader is None:
        raise PyCppError(f"Could not create import spec for: {pyd_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


def inject_public_symbols(module: ModuleType, target_globals: dict) -> None:
    for k, v in module.__dict__.items():
        if k.startswith("__"):
            continue
        target_globals[k] = v


def _add_dll_search_dirs(pyd_path: Path) -> None:
    dirs: list[Path] = [pyd_path.parent, Path(sys.executable).parent, Path(sys.base_prefix)]

    gpp = shutil.which("g++")
    if gpp:
        dirs.append(Path(gpp).parent)

    vcpkg = get_vcpkg_flags()
    for b in vcpkg.bin_dirs:
        dirs.append(b)

    # Windows 10+ prefers AddDllDirectory; fallback to PATH modification.
    for d in dirs:
        try:
            os.add_dll_directory(str(d))
        except (AttributeError, FileNotFoundError):
            pass

    path = os.environ.get("PATH", "")
    for d in dirs:
        ds = str(d)
        if ds and ds not in path:
            path = ds + os.pathsep + path
    os.environ["PATH"] = path
