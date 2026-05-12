# Troubleshooting

## Compiler not found

Set `PY_CPP_CXX` to a compiler on your system:

```bash
export PY_CPP_CXX=clang++
```

or ensure `g++`/`clang++` is on `PATH`.

## ImportError / missing shared libraries

### Windows

If you see `ImportError: DLL load failed`, ensure your MinGW runtime DLLs are available on `PATH`.

`py_cpp_pair` attempts to add (import name: `py_cpp`):

- the build output directory
- the Python executable directory
- the compiler `bin` directory
- vcpkg triplet `bin` directory (if configured)

### Linux/macOS

If a dependent `.so`/`.dylib` cannot be found, ensure the library is installed and discoverable. For vcpkg builds, install the port and retry so the library is located under `vcpkg/installed/<triplet>`.

## vcpkg bootstrap failure

Ensure:

- Git is installed and on `PATH`
- You have network access to clone vcpkg

Alternatively set `VCPKG_ROOT` to an existing vcpkg checkout.
