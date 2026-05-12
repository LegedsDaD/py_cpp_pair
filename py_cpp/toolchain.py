from __future__ import annotations

import os
import platform
import shutil
import sys
from dataclasses import dataclass

from .errors import CompilerNotFoundError, PyCppError
from .logging_utils import get_logger
from .utils import run

log = get_logger(__name__)


@dataclass(frozen=True)
class ToolchainResult:
    installed: bool
    message: str


def auto_install_enabled() -> bool:
    """
    Opt-in only. Installing compilers modifies the system and may require admin rights.
    Enable with env var:
      PY_CPP_AUTO_INSTALL_COMPILER=1
    """
    return os.environ.get("PY_CPP_AUTO_INSTALL_COMPILER", "").strip() in {"1", "true", "TRUE", "yes", "YES"}


def ensure_compiler_available() -> None:
    """
    If a compiler is missing and auto-install is enabled, attempt to install it.
    Always raises CompilerNotFoundError if no compiler is available after attempts.
    """
    if _which("g++") or _which("clang++"):
        return

    if auto_install_enabled():
        res = try_install_compiler()
        log.info(res.message)

    if _which("g++") or _which("clang++"):
        return

    raise CompilerNotFoundError(_missing_compiler_instructions())


def try_install_compiler() -> ToolchainResult:
    """
    Best-effort compiler installation.
    This cannot be fully universal or non-interactive on all platforms.
    """
    sysname = platform.system()
    if sysname == "Linux":
        return _try_install_linux()
    if sysname == "Darwin":
        return _try_install_macos()
    if sysname == "Windows":
        return _try_install_windows()
    return ToolchainResult(False, f"Auto-install not supported on platform: {sysname}")


def _try_install_linux() -> ToolchainResult:
    # Prefer clang++ as requested; fall back to g++.
    if _which("apt-get"):
        cmd = ["sudo", "apt-get", "update"] if _can_use_sudo() else ["apt-get", "update"]
        _run_ignore_failure(cmd)
        cmd2 = (
            ["sudo", "apt-get", "install", "-y", "clang", "g++"]
            if _can_use_sudo()
            else ["apt-get", "install", "-y", "clang", "g++"]
        )
        ok = _run_ignore_failure(cmd2)
        return ToolchainResult(ok, "Attempted to install clang/g++ via apt-get.")

    if _which("dnf"):
        cmd = ["sudo", "dnf", "install", "-y", "clang", "gcc-c++"] if _can_use_sudo() else ["dnf", "install", "-y", "clang", "gcc-c++"]
        ok = _run_ignore_failure(cmd)
        return ToolchainResult(ok, "Attempted to install clang/g++ via dnf.")

    if _which("yum"):
        cmd = ["sudo", "yum", "install", "-y", "clang", "gcc-c++"] if _can_use_sudo() else ["yum", "install", "-y", "clang", "gcc-c++"]
        ok = _run_ignore_failure(cmd)
        return ToolchainResult(ok, "Attempted to install clang/g++ via yum.")

    if _which("pacman"):
        cmd = ["sudo", "pacman", "-Syu", "--noconfirm", "clang", "gcc"] if _can_use_sudo() else ["pacman", "-Syu", "--noconfirm", "clang", "gcc"]
        ok = _run_ignore_failure(cmd)
        return ToolchainResult(ok, "Attempted to install clang/g++ via pacman.")

    return ToolchainResult(False, "No supported Linux package manager detected for auto-install.")


def _try_install_macos() -> ToolchainResult:
    # Xcode CLT install can be interactive; we still attempt a trigger.
    if _which("xcode-select"):
        ok = _run_ignore_failure(["xcode-select", "--install"])
        return ToolchainResult(ok, "Attempted to trigger Xcode Command Line Tools install (may be interactive).")

    if _which("brew"):
        ok = _run_ignore_failure(["brew", "install", "llvm"])
        return ToolchainResult(ok, "Attempted to install llvm (clang) via Homebrew.")

    return ToolchainResult(False, "No supported macOS installer detected (xcode-select or brew).")


def _try_install_windows() -> ToolchainResult:
    # Prefer LLVM clang via winget if available.
    if _which("winget"):
        ok = _run_ignore_failure(["winget", "install", "-e", "--id", "LLVM.LLVM", "--accept-source-agreements", "--accept-package-agreements"])
        return ToolchainResult(ok, "Attempted to install LLVM (clang) via winget.")

    # MSYS2 is a common route, but installing it automatically is environment-specific.
    return ToolchainResult(False, "Auto-install on Windows requires winget (LLVM.LLVM) or a preinstalled toolchain.")


def _missing_compiler_instructions() -> str:
    sysname = platform.system()
    if sysname == "Windows":
        return (
            "No C++ compiler found.\n"
            "- Install MinGW-w64 g++ (recommended) and add its bin directory to PATH, or install LLVM clang.\n"
            "- Optional auto-install: set PY_CPP_AUTO_INSTALL_COMPILER=1 (uses winget LLVM.LLVM when available)."
        )
    if sysname == "Darwin":
        return (
            "No C++ compiler found.\n"
            "- Install Xcode Command Line Tools: `xcode-select --install`\n"
            "- Optional auto-install: set PY_CPP_AUTO_INSTALL_COMPILER=1 (may still be interactive)."
        )
    if sysname == "Linux":
        return (
            "No C++ compiler found.\n"
            "- Install g++ or clang++ via your package manager.\n"
            "- Optional auto-install: set PY_CPP_AUTO_INSTALL_COMPILER=1 (best-effort via apt/dnf/yum/pacman)."
        )
    return f"No C++ compiler found for platform: {sysname}"


def _can_use_sudo() -> bool:
    if os.geteuid() == 0:  # type: ignore[attr-defined]
        return False
    return _which("sudo") is not None


def _run_ignore_failure(cmd: list[str]) -> bool:
    try:
        run(cmd)
        return True
    except PyCppError:
        return False


def _which(exe: str) -> str | None:
    return shutil.which(exe)
