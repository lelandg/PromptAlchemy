"""
Logging configuration for PromptAlchemy.

Provides rotating file handlers with automatic log rotation in the AppData folder.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logging(config_dir: Path, log_level: str = "INFO", console_output: bool = True) -> Path:
    """
    Set up application-wide logging with rotation.

    Args:
        config_dir: Configuration directory (from ConfigManager)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Whether to also output to console

    Returns:
        Path to the log file
    """
    # Create logs directory
    logs_dir = config_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Log file path
    log_file = logs_dir / "promptalchemy.log"

    # Convert log level string to constant
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create rotating file handler
    # Max size: 10MB per file, keep 5 backup files
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)  # Console shows INFO and above
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("=" * 70)
    logger.info("PromptAlchemy Logging Initialized")
    logger.info(f"Log Level: {log_level.upper()}")
    logger.info(f"Log File: {log_file}")
    logger.info(f"Max Size: 10MB per file, {5} backup files")
    logger.info("=" * 70)

    return log_file


def log_exception(logger: logging.Logger, exc: Exception, context: str = ""):
    """
    Log an exception with full traceback.

    Args:
        logger: Logger instance
        exc: Exception to log
        context: Additional context about where the exception occurred
    """
    if context:
        logger.error(f"Exception in {context}: {exc}", exc_info=True)
    else:
        logger.error(f"Exception: {exc}", exc_info=True)


def log_api_call(logger: logging.Logger, provider: str, model: str, success: bool,
                 tokens: Optional[int] = None, error: Optional[str] = None):
    """
    Log an API call for auditing and debugging.

    Args:
        logger: Logger instance
        provider: Provider name
        model: Model name
        success: Whether the call succeeded
        tokens: Number of tokens used (if applicable)
        error: Error message (if failed)
    """
    if success:
        msg = f"API Call Success - Provider: {provider}, Model: {model}"
        if tokens:
            msg += f", Tokens: {tokens}"
        logger.info(msg)
    else:
        msg = f"API Call Failed - Provider: {provider}, Model: {model}"
        if error:
            msg += f", Error: {error}"
        logger.error(msg)


def log_config_change(logger: logging.Logger, key: str, old_value: any, new_value: any):
    """
    Log a configuration change.

    Args:
        logger: Logger instance
        key: Configuration key that changed
        old_value: Previous value
        new_value: New value
    """
    # Mask sensitive values
    if 'key' in key.lower() or 'password' in key.lower() or 'token' in key.lower():
        old_str = "***" if old_value else "None"
        new_str = "***" if new_value else "None"
    else:
        old_str = str(old_value)
        new_str = str(new_value)

    logger.info(f"Config Changed - {key}: {old_str} -> {new_str}")


def get_log_files(config_dir: Path) -> list[Path]:
    """
    Get all log files in the logs directory.

    Args:
        config_dir: Configuration directory

    Returns:
        List of log file paths, sorted by modification time (newest first)
    """
    logs_dir = config_dir / "logs"
    if not logs_dir.exists():
        return []

    log_files = sorted(
        logs_dir.glob("*.log*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    return log_files


def get_recent_logs(config_dir: Path, lines: int = 100) -> str:
    """
    Get the most recent log entries.

    Args:
        config_dir: Configuration directory
        lines: Number of lines to retrieve

    Returns:
        String containing the most recent log entries
    """
    log_file = config_dir / "logs" / "promptalchemy.log"
    if not log_file.exists():
        return "No log file found"

    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:]
            return ''.join(recent_lines)
    except Exception as e:
        return f"Error reading log file: {e}"


# Example usage:
if __name__ == "__main__":
    from core.config import ConfigManager

    config = ConfigManager()
    log_file = setup_logging(config.config_dir, "DEBUG")

    logger = logging.getLogger(__name__)
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    try:
        raise ValueError("Test exception")
    except Exception as e:
        log_exception(logger, e, "test_function")

    log_api_call(logger, "openai", "gpt-4", True, tokens=1500)
    log_api_call(logger, "anthropic", "claude-3", False, error="API key not found")
    log_config_change(logger, "default_model", "gpt-3.5", "gpt-4")
    log_config_change(logger, "api_key", "old_key", "new_key")

    print(f"\nLog file created at: {log_file}")
    print("\nRecent logs:")
    print(get_recent_logs(config.config_dir, 20))
