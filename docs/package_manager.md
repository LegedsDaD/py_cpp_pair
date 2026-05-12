# Package manager (vcpkg)

`py_cpp_pair` uses **vcpkg** to install third-party C++ libraries (import name: `py_cpp`).

## Install a library

```python
import py_cpp as pcp

pcp.install("fmt")
```

## Triplets

`py_cpp_pair` chooses a default triplet by platform:

- Windows: `x64-mingw-dynamic`
- Linux: `x64-linux` (or `arm64-linux`)
- macOS: `x64-osx` (or `arm64-osx`)

The chosen triplet is saved in the metadata file so compilation can reuse the same installed tree.

## How compile integration works

During compilation:

- `dependency_manager.get_vcpkg_flags()` adds `-I<installed>/include`
- Adds `-L<installed>/lib`
- Adds `-l<package>` when a matching library file is detected
- Adds vcpkg `bin` directories to DLL search paths (Windows) and runtime `PATH`

Auto-linking is best-effort by design. Some ports produce multiple libraries or non-standard names; in those cases, you may need to adapt your C++ code accordingly or install a different port configuration.
