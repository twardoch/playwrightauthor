#!/usr/bin/env -S uv run --quiet
# this_file: examples/example_adaptive_timing.py
"""
Example demonstrating adaptive timing for UI interactions.

The AdaptiveTimingController speeds up after consecutive successes
and slows down after failures, making automation resilient to variable
UI response times.
"""

from playwrightauthor import Browser
from playwrightauthor.helpers.timing import AdaptiveTimingController


def main():
    """Demonstrate adaptive timing with real UI interactions."""
    print("=== Adaptive Timing Example ===\n")

    # Create timing controller (starts with default timing)
    timing = AdaptiveTimingController()

    print(f"Initial wait time: {timing.wait_after_click}s\n")
    print(f"Initial timeout: {timing.sync_timeout_ms}ms\n")

    with Browser(verbose=False) as browser:
        page = browser.get_page()

        # Navigate to a test page
        page.goto("https://example.com")
        print("✓ Navigated to example.com")

        # Simulate a series of UI interactions with adaptive timing
        for i in range(5):
            try:
                # Get current timings
                wait_time, timeout = timing.get_timings()
                print(
                    f"\nIteration {i + 1}: Wait={wait_time:.2f}s, Timeout={timeout}ms"
                )

                # Wait before interaction
                page.wait_for_timeout(int(wait_time * 1000))

                # Try to find an element
                heading = page.query_selector("h1")
                if heading:
                    print(f"✓ Found heading: {heading.inner_text()}")
                    # Mark success to speed up after 3 consecutive successes
                    timing.on_success()
                    print(
                        f"  → Success count: {timing.consecutive_successes}/3 needed to speed up"
                    )
                else:
                    # Mark failure to slow down
                    timing.on_failure()
                    print("  → Failed! Timing slowed down")

            except Exception as e:
                print(f"✗ Error: {e}")
                timing.on_failure()
                print("  → Error! Timing slowed down")

        # Show final timing state
        print("\n=== Final Timing State ===")
        final_wait, final_timeout = timing.get_timings()
        print(f"Wait after click: {final_wait:.2f}s")
        print(f"Sync timeout: {final_timeout}ms")
        print(f"Consecutive successes: {timing.consecutive_successes}")
        print(f"Consecutive failures: {timing.consecutive_failures}")


if __name__ == "__main__":
    main()
