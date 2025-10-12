#!/usr/bin/env python3
"""
PromptAlchemy - LLM Prompt Enhancer
Main GUI entry point.
"""

import sys
import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.config import ConfigManager
from core.logging_config import setup_logging, log_exception


def main():
    """Main application entry point."""
    try:
        # Initialize configuration first
        config = ConfigManager()

        # Set up logging with rotation
        log_file = setup_logging(
            config.config_dir,
            log_level="INFO",
            console_output=True
        )

        logger = logging.getLogger(__name__)
        logger.info("Starting PromptAlchemy...")
        logger.info(f"Configuration directory: {config.config_dir}")

        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("PromptAlchemy")
        app.setOrganizationName("PromptAlchemy")

        # Import GUI after logging is set up
        from gui.main_window import PromptAlchemyMainWindow

        # Create and show main window
        window = PromptAlchemyMainWindow()
        window.show()

        logger.info("PromptAlchemy started successfully")

        # Run application
        result = app.exec()
        logger.info("PromptAlchemy exiting")
        return result

    except Exception as e:
        # Critical startup error
        error_msg = f"Critical error during startup: {e}"
        print(error_msg, file=sys.stderr)

        # Try to log it if possible
        try:
            logger = logging.getLogger(__name__)
            log_exception(logger, e, "main startup")
        except:
            pass

        # Show error dialog
        try:
            app = QApplication.instance() or QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Startup Error",
                f"PromptAlchemy failed to start:\n\n{error_msg}\n\nCheck logs for details."
            )
        except:
            pass

        return 1


if __name__ == '__main__':
    main()
