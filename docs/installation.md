# Installation

## Python

`py_cpp_pair` supports Python **3.10–3.13** (import name: `py_cpp`).

Install in editable mode for development:

```bash
pip install -e .
```

## C++ compiler setup

`py_cpp_pair` compiles C++ at runtime. You must have a working C++ compiler on `PATH`.

### Optional: best-effort auto-install

Because installing compilers modifies your system and often requires admin rights, `py_cpp_pair` does **not** auto-install by default.

You can opt in by setting `PY_CPP_AUTO_INSTALL_COMPILER=1`:

```bash
# The installer logic is OS-aware and chooses the best available path.

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

Behavior:
- Linux: tries apt/dnf/yum/pacman to install `clang` and `g++`
- macOS: tries `xcode-select --install` (may be interactive) or `brew install llvm` if Homebrew exists
- Windows: tries `winget install LLVM.LLVM` if winget is available
- After any installer runs, you may need to open a new terminal so your `PATH` updates are visible.

### Windows (MinGW-w64)

Recommended: MSYS2 UCRT64 toolchain.

Verify:

```bash
g++ --version
```

### Linux

Install build tools:

```bash
sudo apt-get update
sudo apt-get install -y g++
```

Verify:

```bash
g++ --version
```

### macOS

Install Xcode Command Line Tools:

```bash
xcode-select --install
```

Verify:

```bash
clang++ --version
```

## vcpkg

`py_cpp_pair` uses vcpkg to install C++ libraries for you.

Detection order:

1. `VCPKG_ROOT` environment variable
2. `vcpkg` available on `PATH`
3. Managed install under your `py_cpp` home directory

If vcpkg is missing and Git is installed, `py_cpp_pair` can bootstrap vcpkg automatically.
