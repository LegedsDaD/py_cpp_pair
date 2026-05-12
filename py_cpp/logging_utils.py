from __future__ import annotations

import logging
from pathlib import Path


def get_logger(name: str = "py_cpp") -> logging.Logger:
    return logging.getLogger(name)


def configure_logging(*, log_level: str = "INFO", log_file: Path | None = None) -> None:
    logger = logging.getLogger("py_cpp")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logger.propagate = False

    if not logger.handlers:
        handler: logging.Handler
        if log_file is not None:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            handler = logging.FileHandler(log_file, encoding="utf-8")
        else:
            handler = logging.StreamHandler()

        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)

