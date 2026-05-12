# py_cpp_pair

Write C++ directly inside Python strings, auto-generate `pybind11` bindings, compile on-demand, dynamically load the extension, and inject exported symbols into your Python globals.

**Version:** `1.0.0`

## Badges

- PyPI: `py_cpp_pair 1.0.0` (import name: `py_cpp`)
- Python: 3.10–3.13
- Platforms: Windows / Linux / macOS
- CI: GitHub Actions

## Install

```bash
pip install py_cpp_pair
```

Import name stays:

```python
import py_cpp as pcp
```

## Quickstart

```python
import py_cpp as pcp

pcp.cpp("""
int add(int a, int b) {
    return a + b;
}
""")

print(add(5, 7))  # 12
```

## Class support

```python
import py_cpp as pcp

pcp.cpp(r"""
class Robot {
public:
    int power = 100;
    Robot() {}
    int attack() { return power * 2; }
};
""")

r = Robot()
print(r.attack())  # 200
```

## Public API

Only these are intended as public:

- `pcp.cpp(code: str) -> module`
- `pcp.install(package: str) -> bool`
- `pcp.clear_cache() -> None`
- `pcp.version() -> str`

## Cross-platform support

| OS | Compiler used | Notes |
|---|---|---|
| Windows | MinGW-w64 `g++` (preferred) | Requires `g++` on `PATH`. |
| Linux | `g++` | Requires build tools installed. |
| macOS | `clang++` | Requires Xcode Command Line Tools. |

Override the compiler via:

```bash
# Windows (PowerShell)
$env:PY_CPP_CXX = "g++"

# Windows (cmd.exe)
set PY_CPP_CXX=g++

# Linux/macOS (bash/zsh)
export PY_CPP_CXX=clang++
```

Optional best-effort auto-install (opt-in):

```bash
# Enable by setting an environment variable in your shell.
# The installer logic is OS-aware (Linux/macOS/Windows) and picks the best available path.

# Windows (PowerShell)
$env:PY_CPP_AUTO_INSTALL_COMPILER = "1"

# Windows (cmd.exe)
set PY_CPP_AUTO_INSTALL_COMPILER=1

# Linux/macOS (bash/zsh)
export PY_CPP_AUTO_INSTALL_COMPILER=1
```

One-shot (only for a single command):

```bash
# Windows (PowerShell)
$env:PY_CPP_AUTO_INSTALL_COMPILER="1"; python -c "import py_cpp.toolchain as t; t.ensure_compiler_available(); print('compiler ok')"

# Linux/macOS (bash/zsh)
PY_CPP_AUTO_INSTALL_COMPILER=1 python -c "import py_cpp.toolchain as t; t.ensure_compiler_available(); print('compiler ok')"
```

Note: after an installer runs, you may need to open a new terminal so `PATH` updates are visible.

## vcpkg package management

Install a C++ library with:

```python
import py_cpp as pcp
pcp.install("fmt")
```

If the port does not exist:

```text
Sorry, library not found.
```

`py_cpp_pair` detects `vcpkg` via `VCPKG_ROOT` or `PATH`. If missing, it can auto-bootstrap by cloning vcpkg (requires Git).

## Caching and build layout

`py_cpp_pair` caches builds by SHA256 hash of the C++ source. Reusing identical code reuses the compiled extension.

Per-user state is stored under `PY_CPP_HOME` if set, otherwise the OS-default data directory:

- Windows: `%LOCALAPPDATA%\\py_cpp`
- macOS: `~/Library/Application Support/py_cpp`
- Linux: `$XDG_DATA_HOME/py_cpp` or `~/.local/share/py_cpp`

Subfolders:

- `builds/`: compiled extensions per hash
- `cache/`: toolchain artifacts (Windows Python import libs)
- `logs/`: optional logs (enable with `PY_CPP_LOG_FILE=1`)

## Troubleshooting

- **ImportError: DLL load failed (Windows)**: ensure MinGW runtime DLLs are visible. `py_cpp_pair` adds common DLL dirs automatically, but the compiler `bin` directory must be on `PATH`.
- **No compiler found**: install `g++`/`clang++` and ensure it is on `PATH`.
- **vcpkg bootstrap fails**: install Git and retry, or set `VCPKG_ROOT` to an existing vcpkg checkout.

## Performance notes

- Compilation is cached by source hash; repeated calls are fast after the first build.
- For larger projects, prefer fewer, bigger `cpp()` calls (each call creates a module).

## Documentation

See `docs/`:

- `docs/installation.md`
- `docs/architecture.md`
- `docs/api.md`
- `docs/package_manager.md`
- `docs/troubleshooting.md`
- `docs/examples.md`

## Roadmap

- Better symbol detection (still regex-based by design)
- Multiple translation units / headers
- Better vcpkg library auto-linking
- Optional clang-based parsing for richer bindings

## Contributing

See `CONTRIBUTING.md`.

## Release (GitHub Actions)

This repo uses a single manual workflow: `.github/workflows/release.yml`.

- **Mode = `check`**: builds `sdist`/`wheel` and runs `twine check` (no publishing).
- **Mode = `publish`**: runs the same checks, then creates a GitHub Release and publishes to PyPI using **Trusted Publishing** (OIDC).

Trusted Publishing setup (one-time):

- In your PyPI project settings, add this GitHub repo as a **Trusted Publisher** (no `PYPI_API_TOKEN` secret needed).
