# this_file: tests/test_benchmark.py
import pytest

from playwrightauthor.browser_manager import ensure_browser


@pytest.mark.benchmark(group="ensure_browser")
def test_benchmark_ensure_browser(benchmark):
    """Benchmark the ensure_browser function."""
    benchmark(ensure_browser, verbose=False)
