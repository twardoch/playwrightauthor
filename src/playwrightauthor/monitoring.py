# this_file: src/playwrightauthor/monitoring.py

"""Production monitoring and health tracking for PlaywrightAuthor browser instances.

This module provides comprehensive browser health monitoring, crash detection, and
automatic recovery capabilities for both synchronous and asynchronous browser instances.
It's designed to improve reliability for long-running automation tasks by detecting
and recovering from browser crashes, connection failures, and performance degradation.

Key Features:
    - Continuous health monitoring with configurable check intervals
    - Automatic crash detection using process monitoring and CDP health checks
    - Smart recovery with exponential backoff and retry limits
    - Real-time performance metrics (CPU, memory, response times)
    - Thread-safe monitoring for sync browsers, async task-based for async browsers
    - Detailed metrics collection and reporting

Classes:
    BrowserMetrics: Container for performance and health metrics
    BrowserMonitor: Synchronous browser health monitor (uses threading)
    AsyncBrowserMonitor: Asynchronous browser health monitor (uses asyncio)

Usage Example:
    ```python
    from playwrightauthor import Browser

    # Monitoring is automatically enabled by default
    with Browser() as browser:
        page = browser.new_page()
        # If browser crashes, it will automatically restart
        # Metrics are collected and logged on exit

    # Disable monitoring for debugging
    import os
    os.environ['PLAYWRIGHTAUTHOR_MONITORING_ENABLED'] = 'false'
    ```

Configuration:
    Monitoring behavior is controlled via the MonitoringConfig class:
    - enabled: Enable/disable monitoring (default: True)
    - check_interval: Seconds between health checks (default: 30.0)
    - enable_crash_recovery: Auto-restart on crash (default: True)
    - max_restart_attempts: Max restart attempts (default: 3)
    - collect_metrics: Collect performance metrics (default: True)

Environment Variables:
    - PLAYWRIGHTAUTHOR_MONITORING_ENABLED: Enable/disable monitoring
    - PLAYWRIGHTAUTHOR_CHECK_INTERVAL: Override check interval
    - PLAYWRIGHTAUTHOR_ENABLE_CRASH_RECOVERY: Enable/disable crash recovery
"""

import asyncio
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import psutil
from loguru import logger

from .connection import ConnectionHealthChecker


@dataclass
class BrowserMetrics:
    """Container for browser performance metrics."""

    start_time: float = field(default_factory=time.time)
    last_health_check: float = field(default_factory=time.time)
    health_check_count: int = 0
    crash_count: int = 0
    restart_count: int = 0
    memory_usage_mb: float = 0.0
    cpu_percent: float = 0.0
    page_count: int = 0
    response_time_ms: float = 0.0
    is_healthy: bool = True
    last_error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert metrics to dictionary for logging/reporting."""
        uptime = time.time() - self.start_time
        return {
            "uptime_seconds": round(uptime, 2),
            "health_checks": self.health_check_count,
            "crashes": self.crash_count,
            "restarts": self.restart_count,
            "memory_mb": round(self.memory_usage_mb, 2),
            "cpu_percent": round(self.cpu_percent, 2),
            "pages": self.page_count,
            "response_ms": round(self.response_time_ms, 2),
            "healthy": self.is_healthy,
            "last_error": self.last_error,
        }


class BrowserMonitor:
    """Monitors browser health and performance metrics."""

    def __init__(
        self,
        debug_port: int,
        check_interval: float = 30.0,
        on_crash: Callable[[], None] | None = None,
    ):
        """Initialize browser monitor.

        Args:
            debug_port: Chrome debug port to monitor
            check_interval: Seconds between health checks
            on_crash: Callback when browser crash detected
        """
        self.debug_port = debug_port
        self.check_interval = check_interval
        self.on_crash = on_crash
        self.metrics = BrowserMetrics()
        self.health_checker = ConnectionHealthChecker(debug_port)
        self._monitoring = False
        self._monitor_thread: threading.Thread | None = None
        self._browser_pid: int | None = None

    def start_monitoring(self, browser_pid: int | None = None) -> None:
        """Start monitoring browser health in background thread.

        Args:
            browser_pid: Process ID of browser to monitor
        """
        if self._monitoring:
            logger.warning("Browser monitoring already active")
            return

        self._browser_pid = browser_pid
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name=f"BrowserMonitor-{self.debug_port}",
        )
        self._monitor_thread.start()
        logger.info(f"Started browser monitoring on port {self.debug_port}")

    def stop_monitoring(self) -> None:
        """Stop monitoring browser health."""
        if not self._monitoring:
            return

        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        logger.info(f"Stopped browser monitoring on port {self.debug_port}")

    def _monitor_loop(self) -> None:
        """Main monitoring loop running in background thread."""
        while self._monitoring:
            try:
                self._perform_health_check()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                time.sleep(self.check_interval)

    def _perform_health_check(self) -> None:
        """Perform a single health check."""
        self.metrics.health_check_count += 1
        self.metrics.last_health_check = time.time()

        # Check CDP connection health
        diagnostics = self.health_checker.get_connection_diagnostics()
        self.metrics.response_time_ms = diagnostics.get("response_time_ms", 0)
        self.metrics.is_healthy = diagnostics["cdp_available"]

        if not self.metrics.is_healthy:
            self.metrics.last_error = diagnostics.get("error", "Unknown error")
            logger.warning(
                f"Browser unhealthy: {self.metrics.last_error} "
                f"(check #{self.metrics.health_check_count})"
            )

            # Check if browser process crashed
            if self._browser_pid and not self._is_process_alive(self._browser_pid):
                self._handle_crash()
        else:
            self.metrics.last_error = None

        # Collect resource metrics if browser is healthy
        if self.metrics.is_healthy and self._browser_pid:
            self._collect_resource_metrics()

    def _is_process_alive(self, pid: int) -> bool:
        """Check if process is still running."""
        try:
            process = psutil.Process(pid)
            return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def _collect_resource_metrics(self) -> None:
        """Collect CPU and memory metrics for browser process."""
        if not self._browser_pid:
            return

        try:
            process = psutil.Process(self._browser_pid)
            self.metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
            self.metrics.cpu_percent = process.cpu_percent(interval=0.1)

            # Count child processes (pages/tabs)
            children = process.children(recursive=True)
            # Chrome creates multiple helper processes per tab
            self.metrics.page_count = len(
                [p for p in children if "renderer" in p.name().lower()]
            )

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.debug(f"Could not collect metrics for pid {self._browser_pid}: {e}")

    def _handle_crash(self) -> None:
        """Handle detected browser crash."""
        self.metrics.crash_count += 1
        logger.error(
            f"Browser crash detected! (crash #{self.metrics.crash_count}, "
            f"pid: {self._browser_pid})"
        )

        # Call crash handler if provided
        if self.on_crash:
            try:
                self.on_crash()
            except Exception as e:
                logger.error(f"Error in crash handler: {e}")

    def get_metrics(self) -> BrowserMetrics:
        """Get current browser metrics."""
        return self.metrics

    def force_health_check(self) -> bool:
        """Force immediate health check and return status.

        Returns:
            True if browser is healthy, False otherwise
        """
        self._perform_health_check()
        return self.metrics.is_healthy


class AsyncBrowserMonitor:
    """Async version of BrowserMonitor for AsyncBrowser."""

    def __init__(
        self,
        debug_port: int,
        check_interval: float = 30.0,
        on_crash: Callable[[], None] | None = None,
    ):
        """Initialize async browser monitor.

        Args:
            debug_port: Chrome debug port to monitor
            check_interval: Seconds between health checks
            on_crash: Callback when browser crash detected
        """
        self.debug_port = debug_port
        self.check_interval = check_interval
        self.on_crash = on_crash
        self.metrics = BrowserMetrics()
        self.health_checker = ConnectionHealthChecker(debug_port)
        self._monitoring = False
        self._monitor_task: asyncio.Task | None = None
        self._browser_pid: int | None = None

    async def start_monitoring(self, browser_pid: int | None = None) -> None:
        """Start monitoring browser health in background task.

        Args:
            browser_pid: Process ID of browser to monitor
        """
        if self._monitoring:
            logger.warning("Browser monitoring already active")
            return

        self._browser_pid = browser_pid
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info(f"Started async browser monitoring on port {self.debug_port}")

    async def stop_monitoring(self) -> None:
        """Stop monitoring browser health."""
        if not self._monitoring:
            return

        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info(f"Stopped async browser monitoring on port {self.debug_port}")

    async def _monitor_loop(self) -> None:
        """Main monitoring loop running in background task."""
        while self._monitoring:
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in async monitor loop: {e}")
                await asyncio.sleep(self.check_interval)

    async def _perform_health_check(self) -> None:
        """Perform a single health check."""
        self.metrics.health_check_count += 1
        self.metrics.last_health_check = time.time()

        # Check CDP connection health (sync call in thread pool)
        loop = asyncio.get_event_loop()
        diagnostics = await loop.run_in_executor(
            None, self.health_checker.get_connection_diagnostics
        )

        self.metrics.response_time_ms = diagnostics.get("response_time_ms", 0)
        self.metrics.is_healthy = diagnostics["cdp_available"]

        if not self.metrics.is_healthy:
            self.metrics.last_error = diagnostics.get("error", "Unknown error")
            logger.warning(
                f"Browser unhealthy: {self.metrics.last_error} "
                f"(check #{self.metrics.health_check_count})"
            )

            # Check if browser process crashed
            if self._browser_pid:
                is_alive = await loop.run_in_executor(
                    None, self._is_process_alive, self._browser_pid
                )
                if not is_alive:
                    await self._handle_crash()
        else:
            self.metrics.last_error = None

        # Collect resource metrics if browser is healthy
        if self.metrics.is_healthy and self._browser_pid:
            await self._collect_resource_metrics()

    def _is_process_alive(self, pid: int) -> bool:
        """Check if process is still running."""
        try:
            process = psutil.Process(pid)
            return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    async def _collect_resource_metrics(self) -> None:
        """Collect CPU and memory metrics for browser process."""
        if not self._browser_pid:
            return

        loop = asyncio.get_event_loop()

        def _collect_sync():
            try:
                process = psutil.Process(self._browser_pid)
                memory_mb = process.memory_info().rss / 1024 / 1024
                cpu_percent = process.cpu_percent(interval=0.1)

                # Count child processes (pages/tabs)
                children = process.children(recursive=True)
                page_count = len(
                    [p for p in children if "renderer" in p.name().lower()]
                )

                return memory_mb, cpu_percent, page_count
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.debug(
                    f"Could not collect metrics for pid {self._browser_pid}: {e}"
                )
                return None

        result = await loop.run_in_executor(None, _collect_sync)
        if result:
            (
                self.metrics.memory_usage_mb,
                self.metrics.cpu_percent,
                self.metrics.page_count,
            ) = result

    async def _handle_crash(self) -> None:
        """Handle detected browser crash."""
        self.metrics.crash_count += 1
        logger.error(
            f"Browser crash detected! (crash #{self.metrics.crash_count}, "
            f"pid: {self._browser_pid})"
        )

        # Call crash handler if provided
        if self.on_crash:
            try:
                if asyncio.iscoroutinefunction(self.on_crash):
                    await self.on_crash()
                else:
                    self.on_crash()
            except Exception as e:
                logger.error(f"Error in crash handler: {e}")

    def get_metrics(self) -> BrowserMetrics:
        """Get current browser metrics."""
        return self.metrics

    async def force_health_check(self) -> bool:
        """Force immediate health check and return status.

        Returns:
            True if browser is healthy, False otherwise
        """
        await self._perform_health_check()
        return self.metrics.is_healthy
