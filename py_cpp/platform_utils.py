from __future__ import annotations

import os
import platform
import shutil
from dataclasses import dataclass

from .errors import CompilerNotFoundError, PlatformNotSupportedError

@dataclass(frozen=True)
class PlatformInfo:
    system: str  # Windows, Linux, Darwin
    machine: str  # x86_64, arm64, AMD64, etc.

    @property
    def is_windows(self) -> bool:
        return self.system == "Windows"

    @property
    def is_linux(self) -> bool:
        return self.system == "Linux"

    @property
    def is_macos(self) -> bool:
        return self.system == "Darwin"


def get_platform_info() -> PlatformInfo:
    return PlatformInfo(system=platform.system(), machine=platform.machine())


def which(exe: str) -> str | None:
    return shutil.which(exe)


def detect_compiler() -> str:
    """
    Returns a compiler executable name/path.
    Override with env var `PY_CPP_CXX`.
    """
    override = os.environ.get("PY_CPP_CXX")
    if override:
        return override

    # If user opted in, try to install a compiler when missing.
    from .toolchain import ensure_compiler_available

    ensure_compiler_available()

    p = get_platform_info()
    if p.is_windows:
        for cand in ("g++", "clang++"):
            if which(cand):
                return cand
        raise CompilerNotFoundError("No C++ compiler found. Install MinGW-w64 g++ (recommended) and add it to PATH.")

    if p.is_linux:
        for cand in ("g++", "clang++"):
            if which(cand):
                return cand
        raise CompilerNotFoundError("No C++ compiler found. Install g++ or clang++.")

    if p.is_macos:
        for cand in ("clang++", "g++"):
            if which(cand):
                return cand
        raise CompilerNotFoundError("No C++ compiler found. Install Xcode Command Line Tools (clang++).")

    raise PlatformNotSupportedError(f"Unsupported platform: {p.system}")
