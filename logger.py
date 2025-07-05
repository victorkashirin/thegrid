"""
Logging infrastructure for VCV Rack Module Search.

This module provides structured logging with appropriate levels and formatting
to replace print statements throughout the application.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = "vcv_module_search",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Set up a logger with both file and console handlers.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        console_output: Whether to output to console
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "vcv_module_search") -> logging.Logger:
    """
    Get an existing logger or create a new one with default settings.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Set up default logger if none exists
        logger = setup_logger(name)
    return logger


# Default logger instance
default_logger = get_logger()


def log_operation_start(operation: str, logger: Optional[logging.Logger] = None) -> None:
    """Log the start of an operation."""
    if logger is None:
        logger = default_logger
    logger.info(f"Starting {operation}...")


def log_operation_complete(operation: str, logger: Optional[logging.Logger] = None) -> None:
    """Log the completion of an operation."""
    if logger is None:
        logger = default_logger
    logger.info(f"Completed {operation}")


def log_file_operation(action: str, file_path: Path, logger: Optional[logging.Logger] = None) -> None:
    """Log file operations."""
    if logger is None:
        logger = default_logger
    logger.debug(f"{action}: {file_path}")


def log_network_operation(action: str, url: str, logger: Optional[logging.Logger] = None) -> None:
    """Log network operations."""
    if logger is None:
        logger = default_logger
    logger.debug(f"{action}: {url}")


def log_error(message: str, exception: Optional[Exception] = None, logger: Optional[logging.Logger] = None) -> None:
    """Log errors with optional exception details."""
    if logger is None:
        logger = default_logger
    
    if exception:
        logger.error(f"{message}: {str(exception)}")
    else:
        logger.error(message)


def log_warning(message: str, logger: Optional[logging.Logger] = None) -> None:
    """Log warnings."""
    if logger is None:
        logger = default_logger
    logger.warning(message)


def log_progress(current: int, total: int, operation: str, logger: Optional[logging.Logger] = None) -> None:
    """Log progress for long-running operations."""
    if logger is None:
        logger = default_logger
    percentage = (current / total) * 100 if total > 0 else 0
    logger.info(f"{operation}: {current}/{total} ({percentage:.1f}%)")