# Architecture

## High-level flow

1. `pcp.cpp(code)` hashes the C++ source (SHA256).
2. `parser.parse_cpp()` detects basic free functions and simple classes (regex-based MVP parser).
3. `wrapper_generator.generate_wrapper()` emits a single translation unit containing:
   - user C++ code
   - auto-generated `PYBIND11_MODULE(...)` bindings
4. `compiler.compile_extension()` compiles into a Python extension module (`EXT_SUFFIX`).
5. `loader.load_extension_module()` loads the compiled module.
6. `loader.inject_public_symbols()` injects the module’s public symbols into the caller globals.

## Key modules

- `py_cpp/api.py`: public API glue (`cpp`, `install`, `clear_cache`, `version`)
- `py_cpp/parser.py`: symbol extraction
- `py_cpp/wrapper_generator.py`: emits pybind11 wrapper code using `py_cpp/templates/wrapper_template.cpp`
- `py_cpp/compiler.py`: cross-platform compiler abstraction
- `py_cpp/installer.py`: vcpkg bootstrap + install
- `py_cpp/metadata.py`: JSON persistence for installed package metadata
- `py_cpp/dependency_manager.py`: maps installed packages to include/lib/bin flags
- `py_cpp/cache.py`: hashing + build locations
- `py_cpp/loader.py`: dynamic import + symbol injection

