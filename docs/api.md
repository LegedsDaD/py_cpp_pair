# API reference

## `py_cpp.cpp(code: str) -> module`

Compiles `code` (or reuses the cached build), loads the compiled extension module, and injects all public symbols into the caller’s globals.

Typical usage:

```python
import py_cpp as pcp

pcp.cpp("int add(int a,int b){ return a+b; }")
print(add(1, 2))
```

## `py_cpp.install(package: str) -> bool`

Installs a vcpkg port for the current platform triplet and records metadata for future builds.

Returns:
- `True` if install succeeded
- `False` if the port could not be installed (prints `Sorry, library not found.`)

## `py_cpp.clear_cache() -> None`

Deletes per-user cached builds and toolchain artifacts for `py_cpp`.

## `py_cpp.version() -> str`

Returns the installed library version string.

