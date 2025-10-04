# this_file: playwrightauthor/src/playwrightauthor/helpers/timing.py
"""Adaptive timing control for browser automation."""

from dataclasses import dataclass


@dataclass
class AdaptiveTimingController:
    """
    Adaptively control timing based on success/failure patterns.

    Starts optimistic (fast), then adjusts based on whether operations succeed or fail.
    Useful for handling flaky UIs where response times vary significantly.

    Attributes:
        wait_after_click: Seconds to wait after clicking (adjusted dynamically)
        sync_timeout_ms: Milliseconds to wait for sync operations (adjusted dynamically)
        consecutive_successes: Count of recent successes (resets on failure)
        consecutive_failures: Count of recent failures (resets on success)

    Example:
        >>> timing = AdaptiveTimingController()
        >>> # After successful operation:
        >>> timing.on_success()
        >>> wait, timeout = timing.get_timings()
        >>> # After 3 successes, timing speeds up
        >>>
        >>> # After failed operation:
        >>> timing.on_failure()
        >>> wait, timeout = timing.get_timings()
        >>> # Timing slows down immediately

    Note:
        Migrated from application-level code to playwrightauthor for reuse across
        multiple projects. This is a sync-only data class with no I/O.
    """

    wait_after_click: float = 1.0  # Start with 1 second
    sync_timeout_ms: int = 15000  # Start with 15 seconds
    consecutive_successes: int = 0
    consecutive_failures: int = 0

    # Timing bounds
    MIN_WAIT = 0.5
    MAX_WAIT = 5.0
    MIN_TIMEOUT = 10000
    MAX_TIMEOUT = 60000

    def on_success(self) -> None:
        """Called when operation succeeds - try to speed up.

        After 3 consecutive successes, reduces wait time and timeout
        by 20% and 10% respectively, but not below minimum values.
        """
        self.consecutive_successes += 1
        self.consecutive_failures = 0

        # After 3 successes, try to speed up (but not below minimums)
        if self.consecutive_successes >= 3:
            self.wait_after_click = max(self.MIN_WAIT, self.wait_after_click * 0.8)
            self.sync_timeout_ms = max(
                self.MIN_TIMEOUT, int(self.sync_timeout_ms * 0.9)
            )
            self.consecutive_successes = 0

    def on_failure(self) -> None:
        """Called when operation fails - slow down.

        On first failure, doubles wait time and timeout,
        but not above maximum values.
        """
        self.consecutive_failures += 1
        self.consecutive_successes = 0

        # After first failure, slow down significantly
        if self.consecutive_failures == 1:
            self.wait_after_click = min(self.MAX_WAIT, self.wait_after_click * 2.0)
            self.sync_timeout_ms = min(
                self.MAX_TIMEOUT, int(self.sync_timeout_ms * 2.0)
            )

    def get_timings(self) -> tuple[float, int]:
        """Get current wait time and timeout.

        Returns:
            Tuple of (wait_after_click_seconds, sync_timeout_milliseconds)
        """
        return self.wait_after_click, self.sync_timeout_ms
