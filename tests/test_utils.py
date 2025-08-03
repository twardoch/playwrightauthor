# this_file: tests/test_utils.py
import pytest
from pathlib import Path
from playwrightauthor.utils.paths import install_dir
from playwrightauthor.utils.logger import configure

def test_install_dir():
    """Test that install_dir() returns a Path object."""
    path = install_dir()
    assert isinstance(path, Path)
    assert "playwrightauthor" in str(path)

def test_configure_logger():
    """Test that configure() returns a logger object."""
    logger = configure(verbose=True)
    assert hasattr(logger, "info")
    assert hasattr(logger, "debug")
