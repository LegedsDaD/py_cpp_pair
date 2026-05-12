from __future__ import annotations


class PyCppError(RuntimeError):
    """Base error for py_cpp."""


class PlatformNotSupportedError(PyCppError):
    pass


class CompilerNotFoundError(PyCppError):
    pass


class CompilationError(PyCppError):
    pass


class VcpkgError(PyCppError):
    pass


class ParseError(PyCppError):
    pass

