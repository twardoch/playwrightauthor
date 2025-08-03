# this_file: tests/test_platform_specific.py

import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playwrightauthor.browser.finder import (
    _get_linux_chrome_paths,
    _get_macos_chrome_paths,
    _get_windows_chrome_paths,
    find_chrome_executable,
    get_chrome_version,
)
from playwrightauthor.utils.logger import configure


class TestPlatformSpecificChromeFinding:
    """Test Chrome finding functionality on different platforms."""

    def setup_method(self):
        """Set up test logger."""
        self.logger = configure(verbose=True)

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_windows_chrome_paths(self):
        """Test Windows Chrome path generation."""
        paths = list(_get_windows_chrome_paths())

        # Should return multiple paths
        assert len(paths) > 5

        # Should include common Chrome locations
        path_strings = [str(p) for p in paths]
        assert any("Program Files" in p for p in path_strings)
        assert any("chrome.exe" in p for p in path_strings)

        # Should check both 32-bit and 64-bit locations
        assert any("Program Files (x86)" in p for p in path_strings)

    @pytest.mark.skipif(sys.platform != "darwin", reason="macOS-specific test")
    def test_macos_chrome_paths(self):
        """Test macOS Chrome path generation."""
        paths = list(_get_macos_chrome_paths())

        # Should return multiple paths
        assert len(paths) > 5

        # Should include common Chrome locations
        path_strings = [str(p) for p in paths]
        assert any("/Applications/" in p for p in path_strings)
        assert any("Google Chrome" in p for p in path_strings)

        # Should check both system and user applications
        assert any("Applications/Google Chrome.app" in p for p in path_strings)

        # On ARM Macs, should check both architectures
        if platform.machine() == "arm64":
            assert any("chrome-mac-arm64" in p for p in path_strings)
            assert any("chrome-mac-x64" in p for p in path_strings)

    @pytest.mark.skipif(
        not sys.platform.startswith("linux"), reason="Linux-specific test"
    )
    def test_linux_chrome_paths(self):
        """Test Linux Chrome path generation."""
        paths = list(_get_linux_chrome_paths())

        # Should return multiple paths
        assert len(paths) > 10

        # Should include common Chrome locations
        path_strings = [str(p) for p in paths]
        assert any("/usr/bin/" in p for p in path_strings)
        assert any("google-chrome" in p for p in path_strings)

        # Should check snap packages
        assert any("/snap/bin" in p for p in path_strings)

        # Should check various Chrome variants
        assert any("chromium" in p for p in path_strings)
        assert any("google-chrome-stable" in p for p in path_strings)

    def test_find_chrome_executable_with_logger(self):
        """Test find_chrome_executable with logging enabled."""
        # This test runs on all platforms
        result = find_chrome_executable(self.logger)

        # On CI environments, Chrome might not be installed
        # So we just verify the function runs without error
        assert result is None or isinstance(result, Path)

        # If Chrome is found, verify it's a valid path
        if result:
            assert result.exists()
            assert result.is_file()

    @patch("subprocess.run")
    def test_get_chrome_version_success(self, mock_run):
        """Test successful Chrome version retrieval."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Google Chrome 120.0.6099.109\n"
        )

        version = get_chrome_version(Path("/fake/chrome"), self.logger)

        assert version == "Google Chrome 120.0.6099.109"
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_get_chrome_version_failure(self, mock_run):
        """Test Chrome version retrieval failure."""
        mock_run.return_value = MagicMock(returncode=1, stderr="Command not found")

        version = get_chrome_version(Path("/fake/chrome"), self.logger)

        assert version is None

    @patch("subprocess.run")
    def test_get_chrome_version_timeout(self, mock_run):
        """Test Chrome version retrieval timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("chrome", 10)

        version = get_chrome_version(Path("/fake/chrome"), self.logger)

        assert version is None

    def test_find_chrome_unsupported_platform(self):
        """Test Chrome finding on unsupported platform."""
        with patch("sys.platform", "aix"):
            result = find_chrome_executable(self.logger)
            assert result is None


class TestPlatformSpecificPaths:
    """Test platform-specific path handling."""

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_executable_permissions_check(self):
        """Test that executable permissions are checked on Unix systems."""
        with tempfile.NamedTemporaryFile(mode="w", suffix="chrome", delete=False) as f:
            temp_path = Path(f.name)

        try:
            # Make file non-executable
            os.chmod(temp_path, 0o644)

            # Mock the path generator to return our test file
            def mock_paths():
                yield temp_path

            with patch(
                "playwrightauthor.browser.finder._get_linux_chrome_paths", mock_paths
            ):
                result = find_chrome_executable()
                # Should not find the file since it's not executable
                assert result is None

            # Make file executable
            os.chmod(temp_path, 0o755)

            with patch(
                "playwrightauthor.browser.finder._get_linux_chrome_paths", mock_paths
            ):
                result = find_chrome_executable()
                # Now it should find the file
                assert result == temp_path

        finally:
            temp_path.unlink()

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_windows_where_command(self):
        """Test Windows 'where' command integration."""
        # This test verifies that the where command is attempted
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="C:\\Program Files\\Chrome\\chrome.exe\n"
            )

            paths = list(_get_windows_chrome_paths())
            path_strings = [str(p) for p in paths]

            # Verify where command was called
            mock_run.assert_called_with(
                ["where", "chrome.exe"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            # Verify the path from where command is included
            assert "C:\\Program Files\\Chrome\\chrome.exe" in path_strings

    @pytest.mark.skipif(
        not sys.platform.startswith("linux"), reason="Linux-specific test"
    )
    def test_linux_which_command(self):
        """Test Linux 'which' command integration."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="/usr/local/bin/google-chrome\n"
            )

            paths = list(_get_linux_chrome_paths())
            path_strings = [str(p) for p in paths]

            # Verify which command was called
            assert mock_run.called

            # Verify the path from which command is included
            assert "/usr/local/bin/google-chrome" in path_strings


class TestCrossplatformCompatibility:
    """Test cross-platform compatibility features."""

    def test_path_handling(self):
        """Test that Path objects are used consistently."""
        # Test that all path generators return Path objects
        if sys.platform == "win32":
            paths = list(_get_windows_chrome_paths())
        elif sys.platform == "darwin":
            paths = list(_get_macos_chrome_paths())
        else:
            paths = list(_get_linux_chrome_paths())

        # All paths should be Path objects
        assert all(isinstance(p, Path) for p in paths)

    def test_environment_variable_handling(self):
        """Test environment variable handling across platforms."""
        # Test with custom environment variables
        with patch.dict(os.environ, {"LOCALAPPDATA": "/custom/local"}):
            if sys.platform == "win32":
                paths = list(_get_windows_chrome_paths())
                path_strings = [str(p) for p in paths]
                assert any("/custom/local" in p for p in path_strings)

    def test_home_directory_expansion(self):
        """Test home directory handling."""
        if sys.platform == "darwin":
            paths = list(_get_macos_chrome_paths())
            path_strings = [str(p) for p in paths]

            # Should include user-specific paths
            home = str(Path.home())
            assert any(home in p for p in path_strings)


@pytest.mark.integration
class TestIntegrationPlatformSpecific:
    """Integration tests for platform-specific functionality."""

    def test_real_chrome_finding(self):
        """Test finding Chrome on the actual system."""
        logger = configure(verbose=True)
        result = find_chrome_executable(logger)

        # Log the result for debugging
        if result:
            print(f"Found Chrome at: {result}")

            # If Chrome is found, verify we can get its version
            version = get_chrome_version(result, logger)
            if version:
                print(f"Chrome version: {version}")
                assert "chrome" in version.lower() or "chromium" in version.lower()
        else:
            print("Chrome not found on this system")

    def test_browser_manager_integration(self):
        """Test integration with browser_manager module."""
        from playwrightauthor.browser_manager import _DEBUGGING_PORT

        # This is a basic smoke test to ensure imports work
        assert _DEBUGGING_PORT == 9222
