#!/usr/bin/env python

"""
Centralized logging configuration for PICRUSt2 package.

This module provides consistent logging setup across all PICRUSt2 modules
with configurable output levels and formats.
"""

import logging
import os
import sys
from typing import Optional


class PicrustError(Exception):
    """Custom exception class for PICRUSt2 specific errors."""

    pass


class PicrustLogger:
    """Centralized logger configuration for PICRUSt2."""

    def __init__(self, name: str, level: int = logging.INFO):
        """Initialize logger with specified name and level."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """Set up console handler with formatting."""
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.INFO)

        # Format: [TIMESTAMP] LEVEL - MODULE: MESSAGE
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def add_file_handler(self, log_file: str, level: int = logging.DEBUG):
        """Add file handler for detailed logging."""
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        # More detailed format for file logging
        file_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s:%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)

        self.logger.addHandler(file_handler)

    def set_level(self, level: int):
        """Set logging level for all handlers."""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            if (
                isinstance(handler, logging.StreamHandler)
                and handler.stream == sys.stderr
            ):
                handler.setLevel(level)

    def get_logger(self):
        """Return the configured logger instance."""
        return self.logger


def get_picrust_logger(name: str = "picrust2", **kwargs) -> logging.Logger:
    """Get a configured PICRUSt2 logger instance.

    Args:
        name: Logger name (typically __name__)
        kwargs: Additional keyword arguments for logging configuration
            (e.g., log_file, level, verbose, debug)
    Returns:
        Configured logger instance
    """
    if logging.getLogger(name).handlers:
        logger = logging.getLogger(name)
        logger.debug("Using existing logger instance for '%s'", name)
    else:
        logger = setup_logging(
            log_file=kwargs.get("log_file", None),
            log_file_level=kwargs.get("log_file_level", logging.DEBUG),
            level=kwargs.get("level", None),
            verbose=kwargs.get("verbose", False),
            debug=kwargs.get("debug", False),
            name=name,
        )
        logger.debug("Created new logger instance for '%s'", name)

    return logger


def setup_logging(
    verbose: bool = False, debug: bool = False, log_file: Optional[str] = None, **kwargs
) -> logging.Logger:
    """Set up logging for PICRUSt2 scripts.

    Args:
        verbose: Enable verbose (INFO) logging
        debug: Enable debug logging
        log_file: Path to log file for detailed logging

    Returns:
        Configured logger instance
    """
    # Determine logging level
    if kwargs.get("level", None):
        level = kwargs["level"]
    elif debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    # Configure root PICRUSt2 logger
    root_logger = PicrustLogger(name=kwargs.get("name", "picrust2"), level=level)

    # Add file handler if specified
    if log_file:
        root_logger.add_file_handler(
            log_file, level=kwargs.get("log_file_level", logging.DEBUG)
        )

    return root_logger.get_logger()


def log_and_raise(
    logger: logging.Logger, message: str, exception_class: type = PicrustError
) -> None:
    """Log error message and raise exception.

    Replacement for sys.exit() calls.

    Args:
        logger: Logger instance
        message: Error message
        exception_class: Exception class to raise
    """
    logger.error(message)
    raise exception_class(message)


def get_log_file_path(
    output_dir: str, log_filename: str = "", default_filename: str = "picrust2.log"
) -> str:
    """Get full path for log file in specified output directory.

    Args:
        output_dir: Directory to place log file
        log_filename: Name of the log file (default: picrust2.log)
        default_filename: Default log file name if log_filename is not provided

    Returns:
        Full path to log file
    """
    if not log_filename:
        log_filename = default_filename

    log_file_path = os.path.join(output_dir, log_filename)
    if not os.path.exists(os.path.dirname(log_file_path)):
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    return log_file_path
