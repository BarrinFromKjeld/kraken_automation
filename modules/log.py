""""Shared logging functionality."""

import logging

from typing import Optional


def create_logger(name: Optional[str] = None) -> logging.Logger:
    """Create a standardized logger which writes to kraken.log and stdout on INFO level."""
    logger_instance = logging.getLogger(name if name else __name__)
    file_handle = logging.FileHandler("kraken.log")
    stream_handle = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
    file_handle.setFormatter(formatter)
    file_handle.setFormatter(formatter)
    logger_instance.addHandler(file_handle)
    logger_instance.addHandler(stream_handle)
    logger_instance.setLevel(logging.INFO)
    return logger_instance
