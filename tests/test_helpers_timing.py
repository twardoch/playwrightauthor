# this_file: tests/test_helpers_timing.py
"""Tests for helpers.timing module."""

from playwrightauthor.helpers.timing import AdaptiveTimingController


def test_timing_controller_initial_state():
    """Test initial state of AdaptiveTimingController."""
    timing = AdaptiveTimingController()
    assert timing.wait_after_click == 1.0, "Initial wait should be 1.0 seconds"
    assert timing.sync_timeout_ms == 15000, "Initial timeout should be 15000ms"
    assert timing.consecutive_successes == 0
    assert timing.consecutive_failures == 0


def test_timing_controller_speeds_up_after_successes():
    """Test that timing speeds up after 3 consecutive successes."""
    timing = AdaptiveTimingController()

    # First success - no change yet
    timing.on_success()
    assert timing.wait_after_click == 1.0
    assert timing.sync_timeout_ms == 15000

    # Second success - no change yet
    timing.on_success()
    assert timing.wait_after_click == 1.0
    assert timing.sync_timeout_ms == 15000

    # Third success - should speed up
    timing.on_success()
    assert timing.wait_after_click == 0.8  # 1.0 * 0.8
    assert timing.sync_timeout_ms == 13500  # 15000 * 0.9


def test_timing_controller_slows_down_on_first_failure():
    """Test that timing slows down on first failure."""
    timing = AdaptiveTimingController()

    timing.on_failure()
    assert timing.wait_after_click == 2.0  # 1.0 * 2.0
    assert timing.sync_timeout_ms == 30000  # 15000 * 2.0


def test_timing_controller_respects_minimum_bounds():
    """Test that timing doesn't go below minimum values."""
    timing = AdaptiveTimingController(wait_after_click=0.6, sync_timeout_ms=11000)

    # Multiple successes should speed up but not below minimum
    for _ in range(10):
        timing.on_success()
        timing.on_success()
        timing.on_success()

    assert timing.wait_after_click >= timing.MIN_WAIT
    assert timing.sync_timeout_ms >= timing.MIN_TIMEOUT


def test_timing_controller_respects_maximum_bounds():
    """Test that timing doesn't go above maximum values."""
    timing = AdaptiveTimingController(wait_after_click=4.0, sync_timeout_ms=50000)

    # Multiple failures should slow down but not above maximum
    for _ in range(10):
        timing.on_failure()

    assert timing.wait_after_click <= timing.MAX_WAIT
    assert timing.sync_timeout_ms <= timing.MAX_TIMEOUT


def test_timing_controller_resets_counters_on_failure():
    """Test that success counter resets on failure."""
    timing = AdaptiveTimingController()

    # Build up successes
    timing.on_success()
    timing.on_success()
    assert timing.consecutive_successes == 2

    # Failure should reset
    timing.on_failure()
    assert timing.consecutive_successes == 0
    assert timing.consecutive_failures == 1


def test_timing_controller_resets_counters_on_success():
    """Test that failure counter resets on success."""
    timing = AdaptiveTimingController()

    # Build up failures
    timing.on_failure()
    timing.on_failure()
    assert timing.consecutive_failures == 2

    # Success should reset
    timing.on_success()
    assert timing.consecutive_failures == 0
    assert timing.consecutive_successes == 1


def test_timing_controller_get_timings():
    """Test get_timings returns current values."""
    timing = AdaptiveTimingController(wait_after_click=2.5, sync_timeout_ms=20000)

    wait, timeout = timing.get_timings()
    assert wait == 2.5
    assert timeout == 20000


def test_timing_controller_adaptive_behavior():
    """Test realistic adaptive behavior pattern."""
    timing = AdaptiveTimingController()

    # Scenario: Start slow, get faster with successes, then slow down on failure
    initial_wait, initial_timeout = timing.get_timings()

    # Three successes - should speed up
    timing.on_success()
    timing.on_success()
    timing.on_success()
    fast_wait, fast_timeout = timing.get_timings()
    assert fast_wait < initial_wait
    assert fast_timeout < initial_timeout

    # One failure - should slow down
    timing.on_failure()
    slow_wait, slow_timeout = timing.get_timings()
    assert slow_wait > fast_wait
    assert slow_timeout > fast_timeout


def test_timing_controller_with_custom_initial_values():
    """Test AdaptiveTimingController with custom initial values."""
    timing = AdaptiveTimingController(wait_after_click=3.0, sync_timeout_ms=30000)

    assert timing.wait_after_click == 3.0
    assert timing.sync_timeout_ms == 30000

    # Should still adapt from custom values
    timing.on_success()
    timing.on_success()
    timing.on_success()
    wait, timeout = timing.get_timings()
    assert abs(wait - 2.4) < 0.0001  # 3.0 * 0.8 (with floating point tolerance)
    assert timeout == 27000  # 30000 * 0.9
