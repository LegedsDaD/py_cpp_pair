import os
from pathlib import Path

from .api import clear_cache, cpp, install, version
from .config import CONFIG
from .logging_utils import configure_logging

__version__ = "1.0.0"

# Configure logging once on import (can be controlled via env vars).
_level = os.environ.get("PY_CPP_LOG_LEVEL", "INFO")
_log_file = os.environ.get("PY_CPP_LOG_FILE")
if _log_file:
    log_path = CONFIG.logs_dir / "py_cpp.log" if _log_file == "1" else os.fspath(_log_file)
    configure_logging(log_level=_level, log_file=Path(log_path))
else:
    configure_logging(log_level=_level, log_file=None)

__all__ = ["cpp", "install", "clear_cache", "version", "__version__"]
