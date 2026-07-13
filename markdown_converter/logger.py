import logging
import sys
from typing import Literal

_logger: logging.Logger | None = None

_LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


def get_logger(name: str = "mdconverter") -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    _logger = logging.getLogger(name)
    _logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    _logger.addHandler(handler)

    return _logger


def set_level(level: LogLevel | int) -> None:
    logger = get_logger()
    if isinstance(level, str):
        level = _LOG_LEVELS.get(level.upper(), logging.INFO)
    logger.setLevel(level)
