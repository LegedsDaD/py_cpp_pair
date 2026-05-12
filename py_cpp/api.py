from __future__ import annotations

from types import ModuleType

from .cache import get_entry
from .cleanup import clear_builds, clear_cache as _clear_cache
from .compiler import compile_extension
from .loader import inject_public_symbols, load_extension_module
from .parser import parse_cpp
from .runtime import caller_frame
from .wrapper_generator import generate_wrapper


def cpp(code: str) -> ModuleType:
    """
    Compile the given C++ code (cached by SHA256), load the resulting extension module,
    and inject its public symbols into the caller's globals.
    """
    entry = get_entry(code)
    if not entry.pyd_path.exists():
        parsed = parse_cpp(code)
        wrapper = generate_wrapper(user_code=code, parse=parsed, module_name=entry.module_name)
        compile_extension(entry, wrapper.source)

    module = load_extension_module(module_name=entry.module_name, pyd_path=entry.pyd_path)
    frame = caller_frame(skip=2)
    inject_public_symbols(module, frame.f_globals)
    return module


def install(package: str) -> bool:
    from .installer import install as _install

    return _install(package)


def clear_cache() -> None:
    """
    Clears py_cpp build outputs and cache artifacts for this user.
    """
    clear_builds()
    _clear_cache()


def version() -> str:
    from . import __version__

    return __version__
