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
    """Configuration for browser behavior."""
    
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
    """Configuration for network operations."""
    
    download_timeout: int = 300  # seconds
    retry_attempts: int = 3
    retry_delay: float = 1.0  # seconds
    exponential_backoff: bool = True
    proxy: str | None = None
    
    
@dataclass
class PathsConfig:
    """Configuration for file paths."""
    
    data_dir: Path | None = None
    config_dir: Path | None = None
    cache_dir: Path | None = None
    user_data_dir: Path | None = None
    
    
@dataclass
class LoggingConfig:
    """Configuration for logging."""
    
    verbose: bool = False
    log_file: Path | None = None
    log_level: str = "INFO"
    log_format: str = "{time} | {level} | {message}"
    
    
@dataclass
class PlaywrightAuthorConfig:
    """Main configuration class for PlaywrightAuthor."""
    
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
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
            with open(self.config_path, "r", encoding="utf-8") as f:
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
                        
            # Update feature flags
            for key in ["enable_plugins", "enable_connection_pooling", "enable_lazy_loading",
                        "default_profile", "profile_encryption"]:
                if key in data:
                    setattr(config, key, data[key])
                    
        except (json.JSONDecodeError, IOError) as e:
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
                "data_dir": str(config.paths.data_dir) if config.paths.data_dir else None,
                "config_dir": str(config.paths.config_dir) if config.paths.config_dir else None,
                "cache_dir": str(config.paths.cache_dir) if config.paths.cache_dir else None,
                "user_data_dir": str(config.paths.user_data_dir) if config.paths.user_data_dir else None,
            },
            "logging": {
                "verbose": config.logging.verbose,
                "log_file": str(config.logging.log_file) if config.logging.log_file else None,
                "log_level": config.logging.log_level,
                "log_format": config.logging.log_format,
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