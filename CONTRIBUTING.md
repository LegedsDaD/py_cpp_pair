# Contributing to py_cpp_pair

## Development setup

```bash
python -m pip install -e ".[dev]"
```

## Run tests

```bash
python -m unittest discover -s tests -q
```

## Code style

- Keep public API limited to `cpp()` and `install()` (plus `clear_cache()` and `version()`).
- Prefer small, focused modules with type hints.
- Avoid adding heavy dependencies.
