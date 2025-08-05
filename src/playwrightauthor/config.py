# this_file: src/playwrightauthor/config.py

"""Configuration management for PlaywrightAuthor.

This module handles configuration from multiple sources:
1. Default values
2. Configuration files (JSON, TOML)
3. Environment variables
4. Runtime overrides
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from loguru import logger

from .utils.paths import config_dir


@dataclass
class BrowserConfig:
    """
    Configuration for browser behavior and Chrome debugging settings.

    This class controls how PlaywrightAuthor launches and connects to Chrome for Testing.
    Most users will use the defaults, but these settings allow fine-tuning for specific
    use cases like headless automation, custom user agents, or proxy setups.

    Attributes:
        debug_port (int): Port for Chrome DevTools Protocol (CDP) debugging.
            PlaywrightAuthor connects to this port to control the browser.
            Change if port 9222 conflicts with other services. Range: 1-65535.
            Defaults to 9222.

        headless (bool): Whether to run Chrome in headless mode (no visible window).
            Useful for server environments or background automation.
            Set to True for production deployments without displays.
            Defaults to False (visible browser).

        timeout (int): Default timeout for browser operations in milliseconds.
            Applies to page loads, element waits, and network requests.
            Increase for slow networks or complex pages.
            Defaults to 30000 (30 seconds).

        viewport_width (int): Browser window width in pixels.
            Affects responsive design testing and screenshot dimensions.
            Common values: 1920 (desktop), 1280 (laptop), 375 (mobile).
            Defaults to 1280.

        viewport_height (int): Browser window height in pixels.
            Affects page layout and visible content area.
            Common values: 1080, 720, 667 (mobile).
            Defaults to 720.

        user_agent (str | None): Custom User-Agent string for HTTP requests.
            Override browser identification for compatibility or testing.
            Use None for default Chrome user agent.
            Example: "Mozilla/5.0 (compatible; MyBot/1.0)".
            Defaults to None.

        args (list[str]): Additional Chrome command-line arguments.
            Advanced configuration for specific browser features.
            Example: ["--disable-web-security", "--allow-running-insecure-content"].
            See https://peter.sh/experiments/chromium-command-line-switches/.
            Defaults to empty list.

        ignore_default_args (list[str]): Chrome arguments to remove from defaults.
            Use when default Chrome arguments conflict with your use case.
            Example: ["--disable-extensions"] to allow extension usage.
            Defaults to empty list.

    Environment Variables:
        - PLAYWRIGHTAUTHOR_DEBUG_PORT: Override debug_port
        - PLAYWRIGHTAUTHOR_HEADLESS: Set "true" for headless mode
        - PLAYWRIGHTAUTHOR_TIMEOUT: Override timeout in milliseconds

    Examples:
        Production headless configuration:
        >>> config = BrowserConfig(
        ...     headless=True,
        ...     timeout=60000,  # 60 seconds for slow pages
        ...     viewport_width=1920,
        ...     viewport_height=1080
        ... )

        Mobile browser simulation:
        >>> config = BrowserConfig(
        ...     viewport_width=375,
        ...     viewport_height=667,
        ...     user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)"
        ... )

        Custom proxy setup:
        >>> config = BrowserConfig(
        ...     args=["--proxy-server=http://proxy.company.com:8080"]
        ... )
    """

    debug_port: int = 9222
    headless: bool = False
    timeout: int = 30000  # milliseconds
    viewport_width: int = 1280
    viewport_height: int = 720
    user_agent: str | None = None
    args: list[str] = field(default_factory=list)
    ignore_default_args: list[str] = field(default_factory=list)


@dataclass
class NetworkConfig:
    """
    Configuration for network operations and retry behavior.

    Controls how PlaywrightAuthor handles network requests, downloads, and
    connection failures. These settings are crucial for reliable automation
    in environments with unstable network connections or strict firewalls.

    Attributes:
        download_timeout (int): Maximum time to wait for downloads in seconds.
            Applied when downloading Chrome for Testing browser.
            Increase for slow internet connections or large downloads.
            Defaults to 300 (5 minutes).

        retry_attempts (int): Number of retry attempts for failed operations.
            Applies to browser connections, network requests, and downloads.
            Set to 0 to disable retries. Higher values increase reliability
            but may slow down failure detection.
            Defaults to 3.

        retry_delay (float): Base delay between retry attempts in seconds.
            Used as the initial delay. With exponential_backoff=True,
            actual delays will be: 1s, 2s, 4s, etc.
            Defaults to 1.0.

        exponential_backoff (bool): Whether to use exponential backoff for retries.
            When True, retry delays increase exponentially: 1s, 2s, 4s, 8s.
            When False, uses fixed delay for all attempts.
            Exponential backoff is recommended for network operations.
            Defaults to True.

        proxy (str | None): HTTP/HTTPS proxy server URL.
            Format: "http://proxy.example.com:8080" or "https://user:pass@proxy.com:8080".
            Applied to all network requests including browser downloads.
            Use None to disable proxy. Supports authentication credentials.
            Defaults to None.

    Environment Variables:
        - PLAYWRIGHTAUTHOR_PROXY: Set proxy server URL
        - PLAYWRIGHTAUTHOR_RETRY_ATTEMPTS: Override retry_attempts

    Examples:
        High-reliability configuration for unstable networks:
        >>> config = NetworkConfig(
        ...     retry_attempts=5,
        ...     retry_delay=2.0,
        ...     download_timeout=600,  # 10 minutes
        ...     exponential_backoff=True
        ... )

        Corporate proxy setup:
        >>> config = NetworkConfig(
        ...     proxy="http://user:password@proxy.company.com:8080",
        ...     download_timeout=900  # Proxies can be slow
        ... )

        Fast-fail configuration for quick feedback:
        >>> config = NetworkConfig(
        ...     retry_attempts=1,
        ...     retry_delay=0.5,
        ...     download_timeout=60,
        ...     exponential_backoff=False
        ... )
    """

    download_timeout: int = 300  # seconds
    retry_attempts: int = 3
    retry_delay: float = 1.0  # seconds
    exponential_backoff: bool = True
    proxy: str | None = None


@dataclass
class PathsConfig:
    """
    Configuration for file system paths and directory locations.

    Controls where PlaywrightAuthor stores browser installations, profiles,
    configuration files, and cache data. Most users can use the defaults,
    but custom paths are useful for shared systems, containers, or specific
    directory structures.

    Attributes:
        data_dir (Path | None): Root directory for all PlaywrightAuthor data.
            Contains browser installations, profiles, and cache.
            When None, uses platform-appropriate default:
            - macOS: ~/Library/Application Support/playwrightauthor
            - Linux: ~/.local/share/playwrightauthor
            - Windows: %APPDATA%/playwrightauthor
            Defaults to None (auto-detect).

        config_dir (Path | None): Directory for configuration files.
            Stores config.json and other settings files.
            When None, uses platform-appropriate config directory:
            - macOS: ~/Library/Preferences/playwrightauthor
            - Linux: ~/.config/playwrightauthor
            - Windows: %APPDATA%/playwrightauthor
            Defaults to None (auto-detect).

        cache_dir (Path | None): Directory for temporary cache files.
            Used for download caches and temporary browser data.
            When None, uses platform-appropriate cache directory:
            - macOS: ~/Library/Caches/playwrightauthor
            - Linux: ~/.cache/playwrightauthor
            - Windows: %LOCALAPPDATA%/playwrightauthor
            Defaults to None (auto-detect).

        user_data_dir (Path | None): Custom Chrome user data directory.
            Override the default profile storage location.
            Useful for sharing profiles or custom profile organization.
            When None, uses data_dir/profiles/profile_name.
            Defaults to None (auto-managed).

    Environment Variables:
        - PLAYWRIGHTAUTHOR_DATA_DIR: Override data_dir
        - PLAYWRIGHTAUTHOR_USER_DATA_DIR: Override user_data_dir

    Examples:
        Containerized deployment with shared storage:
        >>> config = PathsConfig(
        ...     data_dir=Path("/app/data/playwrightauthor"),
        ...     cache_dir=Path("/tmp/playwrightauthor-cache")
        ... )

        Multi-user system with shared browser installation:
        >>> import os
        >>> user = os.getenv("USER", "testuser")
        >>> config = PathsConfig(
        ...     data_dir=Path("/opt/playwrightauthor"),  # Shared browser
        ...     user_data_dir=Path(f"/home/{user}/browser-profiles")  # Per-user profiles
        ... )

        Development setup with project-local profiles:
        >>> config = PathsConfig(
        ...     user_data_dir=Path("./profiles"),  # Relative to project
        ...     cache_dir=Path("./tmp/cache")
        ... )
    """

    data_dir: Path | None = None
    config_dir: Path | None = None
    cache_dir: Path | None = None
    user_data_dir: Path | None = None


@dataclass
class MonitoringConfig:
    """
    Configuration for browser health monitoring and automatic recovery.

    Controls how PlaywrightAuthor monitors browser health, detects crashes,
    and handles automatic recovery. These settings are essential for long-running
    automation tasks and production reliability.

    Attributes:
        enabled (bool): Whether to enable browser health monitoring.
            When True, monitors browser process health and CDP connection status.
            Adds slight overhead but significantly improves reliability.
            Defaults to True.

        check_interval (float): Seconds between health check cycles.
            Lower values detect issues faster but increase CPU usage.
            Higher values reduce overhead but may delay crash detection.
            Range: 5.0 - 300.0 seconds. Defaults to 30.0.

        enable_crash_recovery (bool): Whether to automatically restart crashed browsers.
            When True, attempts to restart browser after detecting a crash.
            Essential for unattended automation but may hide underlying issues.
            Defaults to True.

        max_restart_attempts (int): Maximum browser restart attempts after crashes.
            Prevents infinite restart loops if browser consistently crashes.
            After this limit, manual intervention is required.
            Range: 0-10. Defaults to 3.

        collect_metrics (bool): Whether to collect performance metrics.
            When True, tracks memory usage, CPU usage, response times, and page counts.
            Useful for performance monitoring and optimization.
            Defaults to True.

        metrics_retention_hours (int): How long to retain metrics history.
            Controls memory usage for long-running processes.
            Older metrics are automatically purged.
            Range: 1-168 hours (1 week). Defaults to 24.

    Environment Variables:
        - PLAYWRIGHTAUTHOR_MONITORING_ENABLED: Enable/disable monitoring
        - PLAYWRIGHTAUTHOR_CHECK_INTERVAL: Override check interval
        - PLAYWRIGHTAUTHOR_ENABLE_CRASH_RECOVERY: Enable/disable crash recovery

    Examples:
        High-reliability production configuration:
        >>> config = MonitoringConfig(
        ...     enabled=True,
        ...     check_interval=15.0,  # Check every 15 seconds
        ...     enable_crash_recovery=True,
        ...     max_restart_attempts=5,
        ...     collect_metrics=True
        ... )

        Development configuration with fast feedback:
        >>> config = MonitoringConfig(
        ...     enabled=True,
        ...     check_interval=5.0,  # Frequent checks for debugging
        ...     enable_crash_recovery=False,  # Fail fast in development
        ...     collect_metrics=True
        ... )

        Minimal overhead configuration:
        >>> config = MonitoringConfig(
        ...     enabled=True,
        ...     check_interval=60.0,  # Check every minute
        ...     enable_crash_recovery=True,
        ...     collect_metrics=False  # Skip metrics collection
        ... )
    """

    enabled: bool = True
    check_interval: float = 30.0  # seconds
    enable_crash_recovery: bool = True
    max_restart_attempts: int = 3
    collect_metrics: bool = True
    metrics_retention_hours: int = 24


@dataclass
class LoggingConfig:
    """
    Configuration for logging behavior and output formatting.

    Controls how PlaywrightAuthor logs debug information, errors, and operational
    messages. Proper logging configuration is essential for troubleshooting
    issues and monitoring automation in production environments.

    Attributes:
        verbose (bool): Enable detailed debug logging output.
            When True, shows browser management steps, connection attempts,
            and detailed error information. Useful for troubleshooting but
            can be noisy in production.
            Defaults to False.

        log_file (Path | None): File path for persistent log storage.
            When specified, logs are written to this file in addition to console.
            Useful for production monitoring and audit trails.
            File is created if it doesn't exist. Use None for console-only logging.
            Defaults to None (no file logging).

        log_level (str): Minimum log level to display.
            Controls which messages are shown based on severity.
            Levels (from most to least verbose):
            - "TRACE": Everything (very noisy)
            - "DEBUG": Detailed debugging information
            - "INFO": General operational information
            - "WARNING": Potential issues that don't stop execution
            - "ERROR": Errors that stop current operation
            - "CRITICAL": Fatal errors that stop the program
            Defaults to "INFO".

        log_format (str): Format string for log message layout.
            Uses loguru format syntax with available fields:
            - {time}: Timestamp (customizable format)
            - {level}: Log level (INFO, ERROR, etc.)
            - {message}: The actual log message
            - {name}: Logger name
            - {function}: Function name where log was called
            - {line}: Line number where log was called
            Defaults to "{time} | {level} | {message}".

    Environment Variables:
        - PLAYWRIGHTAUTHOR_VERBOSE: Set "true" to enable verbose logging
        - PLAYWRIGHTAUTHOR_LOG_LEVEL: Override log_level

    Examples:
        Production logging with file output:
        >>> config = LoggingConfig(
        ...     verbose=False,
        ...     log_level="WARNING",  # Only warnings and errors
        ...     log_file=Path("/var/log/playwrightauthor.log"),
        ...     log_format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        ... )

        Development debugging:
        >>> config = LoggingConfig(
        ...     verbose=True,
        ...     log_level="DEBUG",
        ...     log_format="{time:HH:mm:ss} | {level} | {function}:{line} | {message}"
        ... )

        Minimal production logging:
        >>> config = LoggingConfig(
        ...     verbose=False,
        ...     log_level="ERROR",  # Only errors
        ...     log_format="{time} | {level} | {message}"
        ... )
    """

    verbose: bool = False
    log_file: Path | None = None
    log_level: str = "INFO"
    log_format: str = "{time} | {level} | {message}"


@dataclass
class PlaywrightAuthorConfig:
    """
    Main configuration class for PlaywrightAuthor.

    This is the central configuration object that contains all settings for
    browser behavior, network operations, file paths, logging, and advanced
    features. Most users will use the defaults, but this class provides
    comprehensive control over PlaywrightAuthor's behavior.

    The configuration is loaded from multiple sources in order of precedence:
    1. Default values (lowest priority)
    2. Configuration file (~/.config/playwrightauthor/config.json)
    3. Environment variables (PLAYWRIGHTAUTHOR_*)
    4. Runtime overrides (highest priority)

    Attributes:
        browser (BrowserConfig): Browser behavior and Chrome settings.
            Controls headless mode, timeouts, viewport size, user agent,
            and Chrome command-line arguments.

        network (NetworkConfig): Network operations and retry behavior.
            Controls download timeouts, retry attempts, backoff strategy,
            and proxy settings.

        paths (PathsConfig): File system paths and directory locations.
            Controls where browser installations, profiles, config files,
            and cache data are stored.

        logging (LoggingConfig): Logging behavior and output formatting.
            Controls log levels, file output, verbosity, and message formatting.

        enable_plugins (bool): Enable the plugin system (experimental).
            When True, allows loading and running third-party plugins
            for extended functionality. Currently experimental.
            Defaults to False.

        enable_connection_pooling (bool): Enable browser connection pooling (experimental).
            When True, reuses browser connections across sessions for
            improved performance. Currently experimental.
            Defaults to False.

        enable_lazy_loading (bool): Enable lazy loading of dependencies.
            When True, imports modules only when needed, reducing startup time.
            Recommended for most use cases.
            Defaults to True.

        default_profile (str): Default browser profile name.
            Used when no profile is specified in Browser() or AsyncBrowser().
            Profile names must be valid directory names.
            Defaults to "default".

        profile_encryption (bool): Enable profile data encryption (experimental).
            When True, encrypts sensitive profile data like cookies and tokens.
            Currently experimental and may impact performance.
            Defaults to False.

    Usage Examples:
        Load default configuration:
        >>> from playwrightauthor.config import get_config
        >>> config = get_config()
        >>> config.browser.debug_port
        9222

        Create custom configuration:
        >>> config = PlaywrightAuthorConfig(
        ...     browser=BrowserConfig(headless=True, timeout=60000),
        ...     network=NetworkConfig(retry_attempts=5),
        ...     logging=LoggingConfig(verbose=True, log_level="DEBUG")
        ... )

        Production configuration example:
        >>> config = PlaywrightAuthorConfig(
        ...     browser=BrowserConfig(
        ...         headless=True,
        ...         timeout=45000,
        ...         viewport_width=1920,
        ...         viewport_height=1080
        ...     ),
        ...     network=NetworkConfig(
        ...         retry_attempts=5,
        ...         download_timeout=600,
        ...         proxy="http://proxy.company.com:8080"
        ...     ),
        ...     logging=LoggingConfig(
        ...         verbose=False,
        ...         log_level="INFO",
        ...         log_file=Path("/var/log/playwrightauthor.log")
        ...     ),
        ...     enable_lazy_loading=True
        ... )

        Save configuration to file:
        >>> from playwrightauthor.config import save_config

        Save configuration example (commented to avoid side effects):

        .. code-block:: python

            from playwrightauthor.config import save_config
            save_config(config)  # Saves to ~/.config/playwrightauthor/config.json

    Configuration File Format:
        The configuration file is JSON format with nested sections:
        {
          "browser": {
            "headless": true,
            "timeout": 45000,
            "debug_port": 9222
          },
          "network": {
            "retry_attempts": 5,
            "proxy": "http://proxy.example.com:8080"
          },
          "logging": {
            "verbose": false,
            "log_level": "INFO"
          },
          "enable_lazy_loading": true,
          "default_profile": "production"
        }

    Environment Variable Examples:
        Export configuration via environment variables:

        # doctest: +SKIP
        # In your shell environment:
        # export PLAYWRIGHTAUTHOR_HEADLESS=true
        # export PLAYWRIGHTAUTHOR_TIMEOUT=60000
        # export PLAYWRIGHTAUTHOR_PROXY=http://proxy.company.com:8080
        # export PLAYWRIGHTAUTHOR_VERBOSE=true
        # export PLAYWRIGHTAUTHOR_LOG_LEVEL=DEBUG
    """

    browser: BrowserConfig = field(default_factory=BrowserConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)

    # Feature flags
    enable_plugins: bool = False
    enable_connection_pooling: bool = False
    enable_lazy_loading: bool = True

    # Profile settings
    default_profile: str = "default"
    profile_encryption: bool = False


class ConfigManager:
    """Manages configuration loading and validation."""

    ENV_PREFIX = "PLAYWRIGHTAUTHOR_"
    CONFIG_FILENAME = "config.json"

    def __init__(self, config_path: Path | None = None):
        """Initialize the configuration manager.

        Args:
            config_path: Optional path to configuration file.
        """
        self.config_path = config_path or self._default_config_path()
        self._config: PlaywrightAuthorConfig | None = None

    def _default_config_path(self) -> Path:
        """Get the default configuration file path."""
        return config_dir() / self.CONFIG_FILENAME

    def load(self) -> PlaywrightAuthorConfig:
        """Load configuration from all sources.

        Returns:
            Loaded configuration.
        """
        if self._config is not None:
            return self._config

        # Start with defaults
        config = PlaywrightAuthorConfig()

        # Load from file if exists
        if self.config_path.exists():
            logger.debug(f"Loading config from {self.config_path}")
            self._load_from_file(config)

        # Override with environment variables
        self._load_from_env(config)

        # Validate configuration
        self._validate(config)

        self._config = config
        return config

    def save(self, config: PlaywrightAuthorConfig | None = None) -> None:
        """Save configuration to file.

        Args:
            config: Configuration to save. Uses current config if None.
        """
        if config is None:
            config = self._config or PlaywrightAuthorConfig()

        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dictionary
        config_dict = self._to_dict(config)

        # Write to file
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=2, sort_keys=True)

        logger.info(f"Saved configuration to {self.config_path}")

    def _load_from_file(self, config: PlaywrightAuthorConfig) -> None:
        """Load configuration from file.

        Args:
            config: Configuration object to update.
        """
        try:
            with open(self.config_path, encoding="utf-8") as f:
                data = json.load(f)

            # Update browser config
            if "browser" in data:
                for key, value in data["browser"].items():
                    if hasattr(config.browser, key):
                        setattr(config.browser, key, value)

            # Update network config
            if "network" in data:
                for key, value in data["network"].items():
                    if hasattr(config.network, key):
                        setattr(config.network, key, value)

            # Update paths config
            if "paths" in data:
                for key, value in data["paths"].items():
                    if hasattr(config.paths, key) and value is not None:
                        setattr(config.paths, key, Path(value))

            # Update logging config
            if "logging" in data:
                for key, value in data["logging"].items():
                    if hasattr(config.logging, key):
                        if key == "log_file" and value is not None:
                            value = Path(value)
                        setattr(config.logging, key, value)

            # Update monitoring config
            if "monitoring" in data:
                for key, value in data["monitoring"].items():
                    if hasattr(config.monitoring, key):
                        setattr(config.monitoring, key, value)

            # Update feature flags
            for key in [
                "enable_plugins",
                "enable_connection_pooling",
                "enable_lazy_loading",
                "default_profile",
                "profile_encryption",
            ]:
                if key in data:
                    setattr(config, key, data[key])

        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load config file: {e}")

    def _load_from_env(self, config: PlaywrightAuthorConfig) -> None:
        """Load configuration from environment variables.

        Args:
            config: Configuration object to update.
        """
        # Browser settings
        if port := os.getenv(f"{self.ENV_PREFIX}DEBUG_PORT"):
            config.browser.debug_port = int(port)

        if headless := os.getenv(f"{self.ENV_PREFIX}HEADLESS"):
            config.browser.headless = headless.lower() == "true"

        if timeout := os.getenv(f"{self.ENV_PREFIX}TIMEOUT"):
            config.browser.timeout = int(timeout)

        # Network settings
        if proxy := os.getenv(f"{self.ENV_PREFIX}PROXY"):
            config.network.proxy = proxy

        if retry := os.getenv(f"{self.ENV_PREFIX}RETRY_ATTEMPTS"):
            config.network.retry_attempts = int(retry)

        # Path settings
        if data_dir := os.getenv(f"{self.ENV_PREFIX}DATA_DIR"):
            config.paths.data_dir = Path(data_dir)

        if user_data_dir := os.getenv(f"{self.ENV_PREFIX}USER_DATA_DIR"):
            config.paths.user_data_dir = Path(user_data_dir)

        # Logging settings
        if verbose := os.getenv(f"{self.ENV_PREFIX}VERBOSE"):
            config.logging.verbose = verbose.lower() == "true"

        if log_level := os.getenv(f"{self.ENV_PREFIX}LOG_LEVEL"):
            config.logging.log_level = log_level.upper()

        # Monitoring settings
        if monitoring_enabled := os.getenv(f"{self.ENV_PREFIX}MONITORING_ENABLED"):
            config.monitoring.enabled = monitoring_enabled.lower() == "true"

        if check_interval := os.getenv(f"{self.ENV_PREFIX}CHECK_INTERVAL"):
            config.monitoring.check_interval = float(check_interval)

        if crash_recovery := os.getenv(f"{self.ENV_PREFIX}ENABLE_CRASH_RECOVERY"):
            config.monitoring.enable_crash_recovery = crash_recovery.lower() == "true"

        # Feature flags
        if plugins := os.getenv(f"{self.ENV_PREFIX}ENABLE_PLUGINS"):
            config.enable_plugins = plugins.lower() == "true"

        if pooling := os.getenv(f"{self.ENV_PREFIX}ENABLE_CONNECTION_POOLING"):
            config.enable_connection_pooling = pooling.lower() == "true"

        if lazy := os.getenv(f"{self.ENV_PREFIX}ENABLE_LAZY_LOADING"):
            config.enable_lazy_loading = lazy.lower() == "true"

    def _validate(self, config: PlaywrightAuthorConfig) -> None:
        """Validate configuration values.

        Args:
            config: Configuration to validate.

        Raises:
            ValueError: If configuration is invalid.
        """
        # Validate port range
        if not 1 <= config.browser.debug_port <= 65535:
            raise ValueError(f"Invalid debug port: {config.browser.debug_port}")

        # Validate timeout
        if config.browser.timeout <= 0:
            raise ValueError(f"Invalid timeout: {config.browser.timeout}")

        # Validate viewport dimensions
        if config.browser.viewport_width <= 0 or config.browser.viewport_height <= 0:
            raise ValueError("Invalid viewport dimensions")

        # Validate network settings
        if config.network.retry_attempts < 0:
            raise ValueError(f"Invalid retry attempts: {config.network.retry_attempts}")

        if config.network.retry_delay < 0:
            raise ValueError(f"Invalid retry delay: {config.network.retry_delay}")

        # Validate log level
        valid_levels = ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if config.logging.log_level.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {config.logging.log_level}")

        # Validate monitoring settings
        if not 5.0 <= config.monitoring.check_interval <= 300.0:
            raise ValueError(
                f"Invalid check interval: {config.monitoring.check_interval}"
            )

        if not 0 <= config.monitoring.max_restart_attempts <= 10:
            raise ValueError(
                f"Invalid max restart attempts: {config.monitoring.max_restart_attempts}"
            )

        if not 1 <= config.monitoring.metrics_retention_hours <= 168:
            raise ValueError(
                f"Invalid metrics retention: {config.monitoring.metrics_retention_hours}"
            )

    def _to_dict(self, config: PlaywrightAuthorConfig) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Args:
            config: Configuration to convert.

        Returns:
            Configuration as dictionary.
        """
        return {
            "browser": {
                "debug_port": config.browser.debug_port,
                "headless": config.browser.headless,
                "timeout": config.browser.timeout,
                "viewport_width": config.browser.viewport_width,
                "viewport_height": config.browser.viewport_height,
                "user_agent": config.browser.user_agent,
                "args": config.browser.args,
                "ignore_default_args": config.browser.ignore_default_args,
            },
            "network": {
                "download_timeout": config.network.download_timeout,
                "retry_attempts": config.network.retry_attempts,
                "retry_delay": config.network.retry_delay,
                "exponential_backoff": config.network.exponential_backoff,
                "proxy": config.network.proxy,
            },
            "paths": {
                "data_dir": str(config.paths.data_dir)
                if config.paths.data_dir
                else None,
                "config_dir": str(config.paths.config_dir)
                if config.paths.config_dir
                else None,
                "cache_dir": str(config.paths.cache_dir)
                if config.paths.cache_dir
                else None,
                "user_data_dir": str(config.paths.user_data_dir)
                if config.paths.user_data_dir
                else None,
            },
            "logging": {
                "verbose": config.logging.verbose,
                "log_file": str(config.logging.log_file)
                if config.logging.log_file
                else None,
                "log_level": config.logging.log_level,
                "log_format": config.logging.log_format,
            },
            "monitoring": {
                "enabled": config.monitoring.enabled,
                "check_interval": config.monitoring.check_interval,
                "enable_crash_recovery": config.monitoring.enable_crash_recovery,
                "max_restart_attempts": config.monitoring.max_restart_attempts,
                "collect_metrics": config.monitoring.collect_metrics,
                "metrics_retention_hours": config.monitoring.metrics_retention_hours,
            },
            "enable_plugins": config.enable_plugins,
            "enable_connection_pooling": config.enable_connection_pooling,
            "enable_lazy_loading": config.enable_lazy_loading,
            "default_profile": config.default_profile,
            "profile_encryption": config.profile_encryption,
        }


# Singleton instance
_config_manager: ConfigManager | None = None


def get_config(config_path: Path | None = None) -> PlaywrightAuthorConfig:
    """Get the global configuration.

    Args:
        config_path: Optional configuration file path. Only used on first call.

    Returns:
        Global configuration instance.
    """
    global _config_manager

    if _config_manager is None:
        _config_manager = ConfigManager(config_path)

    return _config_manager.load()


def save_config(config: PlaywrightAuthorConfig) -> None:
    """Save configuration to file.

    Args:
        config: Configuration to save.
    """
    global _config_manager

    if _config_manager is None:
        _config_manager = ConfigManager()

    _config_manager.save(config)
