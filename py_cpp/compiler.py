from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pybind11

from .cache import CacheEntry, save_meta
from .dependency_manager import get_vcpkg_flags
from .errors import CompilationError
from .logging_utils import get_logger
from .platform_utils import detect_compiler
from .utils import (
    PyCppError,
    ensure_dir,
    get_python_build_info,
    get_python_sysconfig_flags,
)

log = get_logger(__name__)


@dataclass(frozen=True)
class CompileResult:
    output_path: Path
    command: list[str]


def compile_extension(entry: CacheEntry, wrapper_source: str) -> CompileResult:
    ensure_dir(entry.build_dir)
    wrapper_path = entry.build_dir / "wrapper.cpp"
    wrapper_path.write_text(wrapper_source, encoding="utf-8")

    cxx = detect_compiler()
    vcpkg = get_vcpkg_flags()
    pycfg = get_python_sysconfig_flags()

    include_dirs = [*pycfg.include_dirs, Path(pybind11.get_include()), Path(pybind11.get_include(user=True))]
    include_dirs.extend(vcpkg.include_dirs)

    library_dirs = [*pycfg.library_dirs]
    library_dirs.extend(vcpkg.library_dirs)

    libraries = [*pycfg.libraries, *vcpkg.libraries]

    cmd: list[str] = [cxx, str(wrapper_path)]
    cmd += ["-std=c++17", "-O2"]

    if os.name != "nt":
        cmd += ["-fPIC"]

    # Build as an extension module
    cmd += ["-shared"]

    for inc in include_dirs:
        cmd.append(f"-I{inc}")

    # Windows: generate a MinGW import lib for Python and link against it.
    if os.name == "nt":
        cache_root = entry.build_dir.parent.parent  # .../home/builds/<hash> -> home
        try:
            pyinfo = get_python_build_info(cache_root)
        except PyCppError as e:
            raise CompilationError(str(e)) from e
        if pyinfo.mingw_import_lib and pyinfo.mingw_import_lib.exists():
            library_dirs.append(pyinfo.mingw_import_lib.parent)
            libraries.insert(0, f"python{pyinfo.version_major}{pyinfo.version_minor}")

    for libdir in library_dirs:
        cmd.append(f"-L{libdir}")

    for lib in libraries:
        cmd.append(f"-l{lib}")

    cmd += pycfg.extra_link_args

    cmd += ["-o", str(entry.pyd_path)]

    env = os.environ.copy()
    # Help runtime locate dependent DLLs (vcpkg bin, compiler runtime)
    if vcpkg.bin_dirs:
        env["PATH"] = os.pathsep.join([*(str(p) for p in vcpkg.bin_dirs), env.get("PATH", "")])

    try:
        subprocess.run(cmd, cwd=str(entry.build_dir), check=True, capture_output=True, text=True, env=env)
    except subprocess.CalledProcessError as e:
        raise CompilationError(
            "Compilation failed:\n"
            f"cmd: {' '.join(cmd)}\n"
            f"stdout:\n{e.stdout}\n"
            f"stderr:\n{e.stderr}\n"
        ) from e

    save_meta(
        entry,
        {
            "module_name": entry.module_name,
            "output": str(entry.pyd_path),
            "wrapper": str(wrapper_path),
            "compiler": cxx,
        },
    )
    return CompileResult(output_path=entry.pyd_path, command=cmd)

