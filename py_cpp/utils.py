from __future__ import annotations

import os
import shutil
import subprocess
import sys
import sysconfig
from dataclasses import dataclass
from pathlib import Path


from .errors import PyCppError


@dataclass(frozen=True)
class PythonBuildInfo:
    version_major: int
    version_minor: int
    include_dir: Path
    plat_include_dir: Path | None
    libs_dir: Path
    python_dll: Path
    mingw_import_lib: Path


def run(cmd: list[str], *, cwd: str | Path | None = None) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            cmd,
            cwd=str(cwd) if cwd is not None else None,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as e:
        raise PyCppError(f"Command not found: {cmd[0]}") from e
    except subprocess.CalledProcessError as e:
        stdout = e.stdout or ""
        stderr = e.stderr or ""
        raise PyCppError(
            "Command failed:\n"
            f"  cmd: {' '.join(cmd)}\n"
            f"  exit: {e.returncode}\n"
            f"  stdout:\n{stdout}\n"
            f"  stderr:\n{stderr}\n"
        ) from e


def which(exe: str) -> str | None:
    return shutil.which(exe)


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_python_build_info(cache_dir: Path) -> PythonBuildInfo:
    major, minor = sys.version_info[:2]
    include_dir = Path(sysconfig.get_paths()["include"])
    plat_inc = sysconfig.get_paths().get("platinclude")
    plat_include_dir = Path(plat_inc) if plat_inc else None
    base_prefix = Path(sys.base_prefix)
    libs_dir = base_prefix / "libs"

    python_dll = Path(sys.executable).with_name(f"python{major}{minor}.dll")
    if not python_dll.exists():
        python_dll = base_prefix / f"python{major}{minor}.dll"
    if not python_dll.exists():
        raise PyCppError(f"Could not find Python DLL (expected python{major}{minor}.dll).")

    import_lib = ensure_python_import_lib(python_dll, cache_dir) if os.name == "nt" else Path("")
    return PythonBuildInfo(
        version_major=major,
        version_minor=minor,
        include_dir=include_dir,
        plat_include_dir=plat_include_dir,
        libs_dir=libs_dir,
        python_dll=python_dll,
        mingw_import_lib=import_lib,
    )


def ensure_python_import_lib(python_dll: Path, cache_dir: Path) -> Path:
    """
    MinGW needs an import library like `libpython311.dll.a`.
    CPython from python.org ships `python311.lib` (MSVC), so we create a MinGW one if missing.
    """
    if os.name != "nt":
        # Not needed on non-Windows toolchains
        return Path("")

    major, minor = sys.version_info[:2]
    out_dir = ensure_dir(cache_dir / "python-importlib")
    out_lib = out_dir / f"libpython{major}{minor}.dll.a"
    if out_lib.exists():
        return out_lib

    if which("gendef") is None or which("dlltool") is None:
        raise PyCppError(
            "MinGW tools `gendef` and `dlltool` are required to build a Python import library."
        )

    def_file = out_dir / f"python{major}{minor}.def"
    run(["gendef", str(python_dll)], cwd=out_dir)
    generated = out_dir / python_dll.with_suffix(".def").name
    if generated.exists() and generated != def_file:
        generated.replace(def_file)

    run(
        [
            "dlltool",
            "-d",
            str(def_file),
            "-l",
            str(out_lib),
            "-D",
            python_dll.name,
        ],
        cwd=out_dir,
    )
    return out_lib


def windows_quote_arg(arg: str) -> str:
    if " " in arg or "\t" in arg:
        return f"\"{arg}\""
    return arg


def get_ext_suffix() -> str:
    suf = sysconfig.get_config_var("EXT_SUFFIX")
    if isinstance(suf, str) and suf:
        return suf
    # Fallback: windows pyd; others so
    return ".pyd" if os.name == "nt" else ".so"


@dataclass(frozen=True)
class PythonSysconfigFlags:
    include_dirs: list[Path]
    library_dirs: list[Path]
    libraries: list[str]
    extra_link_args: list[str]


def get_python_sysconfig_flags() -> PythonSysconfigFlags:
    include_dirs = [Path(sysconfig.get_paths()["include"])]
    plat = sysconfig.get_paths().get("platinclude")
    if plat:
        include_dirs.append(Path(plat))

    library_dirs: list[Path] = []
    libdir = sysconfig.get_config_var("LIBDIR")
    if libdir:
        library_dirs.append(Path(str(libdir)))
    # On Windows, python.org installs have `libs/`
    if os.name == "nt":
        library_dirs.append(Path(sys.base_prefix) / "libs")

    libs: list[str] = []
    # Best-effort: on Windows we explicitly link -lpythonXY (via generated import lib)
    if os.name != "nt":
        # Many linux builds expose pythonXY and expect linking; some distros don't require it.
        ldlib = sysconfig.get_config_var("LDLIBRARY") or ""
        if isinstance(ldlib, str) and ldlib.startswith("lib") and ldlib.endswith((".so", ".a", ".dylib")):
            libs.append(ldlib[3:].split(".", 1)[0])

    extra_link_args: list[str] = []
    if sys.platform == "darwin":
        # Typical extension build uses this to avoid hard linking to libpython.
        extra_link_args.append("-undefined")
        extra_link_args.append("dynamic_lookup")

    return PythonSysconfigFlags(
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libs,
        extra_link_args=extra_link_args,
    )
