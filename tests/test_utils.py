# this_file: tests/test_utils.py

import sys
from pathlib import Path
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playwrightauthor.utils.logger import configure
from playwrightauthor.utils.paths import install_dir


class TestPaths:
    """Test suite for utils.paths module."""

    def test_install_dir_returns_path(self):
        """Test that install_dir() returns a Path object."""
        path = install_dir()
        assert isinstance(path, Path)

    def test_install_dir_contains_app_name(self):
        """Test that install_dir() contains the application name."""
        path = install_dir()
        assert "playwrightauthor" in str(path).lower()

    def test_install_dir_contains_browser_subdir(self):
        """Test that install_dir() includes 'browser' subdirectory."""
        path = install_dir()
        assert path.name == "browser"

    def test_install_dir_is_absolute(self):
        """Test that install_dir() returns an absolute path."""
        path = install_dir()
        assert path.is_absolute()

    def test_install_dir_consistent(self):
        """Test that multiple calls to install_dir() return the same path."""
        path1 = install_dir()
        path2 = install_dir()
        assert path1 == path2

    @patch("playwrightauthor.utils.paths.user_cache_dir")
    def test_install_dir_with_custom_cache_dir(self, mock_cache_dir):
        """Test install_dir() with a custom cache directory."""
        mock_cache_dir.return_value = "/custom/cache"
        path = install_dir()
        assert str(path) == "/custom/cache/browser"
        mock_cache_dir.assert_called_once_with("playwrightauthor")


class TestLogger:
    """Test suite for utils.logger module."""

    def setup_method(self):
        """Set up test fixtures."""
        # Clear any existing loguru handlers
        from loguru import logger

        logger.remove()

    def teardown_method(self):
        """Clean up after tests."""
        from loguru import logger

        logger.remove()

    def test_configure_returns_logger(self):
        """Test that configure() returns a logger object."""
        logger = configure(verbose=False)
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")

    def test_configure_verbose_false(self):
        """Test configure() with verbose=False sets INFO level."""
        with patch("builtins.print") as mock_print:
            logger = configure(verbose=False)
            logger.debug("debug message")
            logger.info("info message")

            # Debug should not be printed, info should be
            calls = [str(call) for call in mock_print.call_args_list]
            debug_printed = any("debug message" in call for call in calls)
            info_printed = any("info message" in call for call in calls)

            assert not debug_printed, (
                "Debug messages should not be printed when verbose=False"
            )
            assert info_printed, "Info messages should be printed when verbose=False"

    def test_configure_verbose_true(self):
        """Test configure() with verbose=True sets DEBUG level."""
        with patch("builtins.print") as mock_print:
            logger = configure(verbose=True)
            logger.debug("debug message")

            # Both debug and info should be printed
            calls = [str(call) for call in mock_print.call_args_list]
            debug_printed = any("debug message" in call for call in calls)

            assert debug_printed, "Debug messages should be printed when verbose=True"

    def test_configure_removes_existing_handlers(self):
        """Test that configure() removes existing loguru handlers."""
        from loguru import logger

        # Add a handler
        logger.add(lambda m: None)
        len(logger._core.handlers)

        # Configure should remove all handlers and add one new one
        configure(verbose=False)
        final_handlers = len(logger._core.handlers)

        assert final_handlers == 1, "Should have exactly one handler after configure()"

    def test_configure_consistent_logger(self):
        """Test that multiple calls to configure() return the same logger."""
        logger1 = configure(verbose=False)
        logger2 = configure(verbose=True)

        # Should be the same logger instance (loguru singleton)
        assert logger1 is logger2

    def test_configure_logging_levels(self):
        """Test different logging levels work correctly."""
        with patch("builtins.print") as mock_print:
            logger = configure(verbose=False)  # INFO level

            logger.debug("debug")
            logger.info("info")
            logger.warning("warning")
            logger.error("error")

            calls = [str(call) for call in mock_print.call_args_list]

            # Only INFO and above should be printed
            assert not any("debug" in call for call in calls)
            assert any("info" in call for call in calls)
            assert any("warning" in call for call in calls)
            assert any("error" in call for call in calls)


# Integration tests
class TestUtilsIntegration:
    """Integration tests for utils modules."""

    def test_logger_can_log_to_install_dir_path(self):
        """Test that logger can handle Path objects from install_dir()."""
        logger = configure(verbose=True)
        path = install_dir()

        # This should not raise any exceptions
        with patch("builtins.print"):
            logger.info(f"Install directory: {path}")
            logger.debug(f"Path type: {type(path)}")

    def test_paths_work_with_different_platforms(self):
        """Test that paths work across different platform scenarios."""
        path = install_dir()

        # Should be able to create parent directories
        assert path.parent is not None

        # Path should be convertible to string
        path_str = str(path)
        assert isinstance(path_str, str)
        assert len(path_str) > 0
