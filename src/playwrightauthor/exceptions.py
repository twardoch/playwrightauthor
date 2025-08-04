# this_file: src/playwrightauthor/exceptions.py

"""
Custom exceptions for PlaywrightAuthor with user-friendly error messages.

All exceptions include helpful troubleshooting guidance and specific commands
to resolve common issues. Each exception provides context about what went wrong
and actionable steps to fix the problem.

For more troubleshooting help, visit:
https://github.com/twardoch/playwrightauthor/blob/main/docs/troubleshooting.md
"""


class PlaywrightAuthorError(Exception):
    """
    Base exception for all PlaywrightAuthor errors.

    This is the parent class for all PlaywrightAuthor-specific exceptions.
    Catch this to handle any PlaywrightAuthor error generically.
    """

    def __init__(
        self,
        message: str,
        suggestion: str = None,
        command: str = None,
        did_you_mean: list[str] | None = None,
        help_link: str = None,
    ):
        """
        Initialize the exception with helpful context.

        Args:
            message: The main error message explaining what went wrong
            suggestion: Helpful suggestion for resolving the issue
            command: Specific command to run to fix the issue
            did_you_mean: List of similar commands/options the user might have meant
            help_link: Link to documentation for this specific error
        """
        self.message = message
        self.suggestion = suggestion
        self.command = command
        self.did_you_mean = did_you_mean
        self.help_link = help_link

        # Build comprehensive error message
        full_message = f"❌ {message}"

        if did_you_mean:
            full_message += "\n\n❓ Did you mean:"
            for alternative in did_you_mean:
                full_message += f"\n  • {alternative}"

        if suggestion:
            full_message += f"\n\n💡 Suggestion: {suggestion}"

        if command:
            full_message += f"\n\n🔧 Try running: {command}"

        if help_link:
            full_message += f"\n\n📚 Learn more: {help_link}"
        else:
            full_message += "\n\n📚 Learn more: https://github.com/twardoch/playwrightauthor#troubleshooting"

        super().__init__(full_message)


class BrowserManagerError(PlaywrightAuthorError):
    """
    Raised for errors related to browser management.

    This covers issues with finding, installing, launching, or connecting
    to Chrome for Testing. Usually indicates problems with the browser
    setup or system configuration.
    """


class BrowserInstallationError(BrowserManagerError):
    """
    Raised when Chrome for Testing installation fails.

    Common causes:
    - Network connectivity issues
    - Insufficient disk space
    - Permission problems
    - Corrupted downloads
    """

    def __init__(
        self,
        message: str,
        suggestion: str = None,
        command: str = None,
        did_you_mean: list[str] | None = None,
    ):
        # Enhance error message based on common patterns
        if "permission" in message.lower() or "access denied" in message.lower():
            suggestion = suggestion or (
                "You don't have permission to install Chrome in the default location. "
                "Try running with elevated permissions or change the installation directory."
            )
            command = command or "sudo playwrightauthor status  # On macOS/Linux"

        elif "network" in message.lower() or "connection" in message.lower():
            suggestion = suggestion or (
                "Network connection failed while downloading Chrome. "
                "Check your internet connection and proxy settings. "
                "If you're behind a corporate firewall, configure your proxy."
            )
            command = (
                command
                or "export HTTPS_PROXY=http://proxy:8080 && playwrightauthor status"
            )

        elif "space" in message.lower() or "disk" in message.lower():
            suggestion = suggestion or (
                "Insufficient disk space to install Chrome (requires ~500MB). "
                "Free up disk space or change the installation directory."
            )
            command = command or "df -h ~/.playwrightauthor  # Check available space"

        else:
            suggestion = suggestion or (
                "Chrome installation failed. This could be due to network issues, "
                "insufficient permissions, or disk space. Clear the cache and try again."
            )
            command = (
                command or "playwrightauthor clear-cache && playwrightauthor status -v"
            )

        super().__init__(
            message,
            suggestion,
            command,
            help_link="https://github.com/twardoch/playwrightauthor/blob/main/docs/installation.md",
        )


class BrowserLaunchError(BrowserManagerError):
    """
    Raised when Chrome for Testing fails to launch.

    Common causes:
    - Port 9222 already in use
    - Insufficient system resources
    - Security restrictions (sandboxing issues)
    - Corrupted browser installation
    """

    def __init__(
        self,
        message: str,
        suggestion: str = None,
        command: str = None,
        did_you_mean: list[str] | None = None,
    ):
        # Provide specific guidance based on error patterns
        if "port" in message.lower() or "9222" in message:
            suggestion = suggestion or (
                "Port 9222 is already in use by another Chrome instance. "
                "Close all Chrome windows or use a different debug port."
            )
            command = command or "lsof -i :9222  # See what's using the port"
            did_you_mean = ["playwrightauthor status --port 9223"]

        elif "sandbox" in message.lower() or "namespace" in message.lower():
            suggestion = suggestion or (
                "Chrome cannot start due to sandboxing restrictions. "
                "This often happens in Docker containers or restricted environments."
            )
            command = command or (
                "export PLAYWRIGHTAUTHOR_HEADLESS=true && playwrightauthor status"
            )

        elif "display" in message.lower() or "x11" in message.lower():
            suggestion = suggestion or (
                "No display found. Chrome needs a display to run in non-headless mode. "
                "Either set up X11 forwarding or use headless mode."
            )
            command = (
                command or "export DISPLAY=:0 || export PLAYWRIGHTAUTHOR_HEADLESS=true"
            )

        elif "crash" in message.lower() or "abnormal" in message.lower():
            suggestion = suggestion or (
                "Chrome crashed during startup. This could be due to corrupted installation "
                "or incompatible system libraries. Try reinstalling."
            )
            command = (
                command or "playwrightauthor clear-cache && playwrightauthor status"
            )

        else:
            suggestion = suggestion or (
                "Chrome failed to start. Check system resources, permissions, "
                "and try running diagnostics to identify the issue."
            )
            command = command or "playwrightauthor diagnose -v"

        super().__init__(
            message,
            suggestion,
            command,
            did_you_mean,
            help_link="https://github.com/twardoch/playwrightauthor/blob/main/docs/troubleshooting.md#browser-launch-issues",
        )


class ProcessKillError(BrowserManagerError):
    """
    Raised when Chrome process termination fails.

    Common causes:
    - Process is stuck or unresponsive
    - Insufficient permissions to kill process
    - Process has important unsaved data
    - System resource constraints
    """

    def __init__(self, message: str, suggestion: str = None, command: str = None):
        if not suggestion:
            suggestion = (
                "Try manually closing Chrome windows first. If that fails, "
                "restart your system to clear stuck processes."
            )
        if not command:
            command = "pkill -f chrome || taskkill /F /IM chrome.exe"
        super().__init__(message, suggestion, command)


class NetworkError(PlaywrightAuthorError):
    """
    Raised for network-related errors.

    Common causes:
    - No internet connection
    - Firewall blocking requests
    - Proxy configuration issues
    - DNS resolution problems
    - Server timeouts
    """

    def __init__(self, message: str, suggestion: str = None, command: str = None):
        if not suggestion:
            suggestion = (
                "Check your internet connection and firewall settings. "
                "For corporate networks, configure proxy settings using environment variables."
            )
        if not command:
            command = (
                "export HTTPS_PROXY=http://your-proxy:8080 && playwrightauthor status"
            )
        super().__init__(message, suggestion, command)


class TimeoutError(PlaywrightAuthorError):
    """
    Raised when operations exceed configured timeout.

    Common causes:
    - Slow network connection
    - Browser taking too long to start
    - Page loading slowly
    - System under heavy load
    """

    def __init__(self, message: str, suggestion: str = None, command: str = None):
        if not suggestion:
            suggestion = (
                "Increase timeout values or check system performance. "
                "For slow networks, consider increasing network timeout settings."
            )
        if not command:
            command = "export PLAYWRIGHTAUTHOR_TIMEOUT=60000 && playwrightauthor status"
        super().__init__(message, suggestion, command)


class ConfigurationError(PlaywrightAuthorError):
    """
    Raised for configuration-related errors.

    Common causes:
    - Invalid configuration values
    - Missing required settings
    - Conflicting configuration options
    - Malformed configuration files
    """

    def __init__(self, message: str, suggestion: str = None, command: str = None):
        if not suggestion:
            suggestion = (
                "Check your configuration file syntax and validate all settings. "
                "Use environment variables for testing different configurations."
            )
        if not command:
            command = "playwrightauthor config show"
        super().__init__(message, suggestion, command)


class AuthenticationError(PlaywrightAuthorError):
    """
    Raised for authentication-related errors.

    Common causes:
    - Session has expired
    - Profile data corrupted
    - Authentication cookies cleared
    - Service requires re-authentication
    """

    def __init__(self, message: str, suggestion: str = None, command: str = None):
        if not suggestion:
            suggestion = (
                "You may need to manually log in again. PlaywrightAuthor will "
                "save your session for future runs once you authenticate."
            )
        if not command:
            command = "playwrightauthor profile show default"
        super().__init__(message, suggestion, command)


class ConnectionError(PlaywrightAuthorError):
    """
    Raised when connection to Chrome fails.

    Common causes:
    - Chrome not running with debug port
    - Network issues preventing connection
    - Chrome crashed after launch
    - Firewall blocking local connections
    """

    def __init__(
        self,
        message: str,
        suggestion: str = None,
        command: str = None,
        did_you_mean: list[str] | None = None,
    ):
        if "refused" in message.lower() or "connect" in message.lower():
            suggestion = suggestion or (
                "Cannot connect to Chrome. Make sure Chrome is running with remote debugging enabled. "
                "PlaywrightAuthor should start it automatically."
            )
            command = command or "playwrightauthor diagnose  # Check Chrome status"

        elif "timeout" in message.lower():
            suggestion = suggestion or (
                "Connection to Chrome timed out. Chrome may be slow to start or unresponsive. "
                "Try increasing the timeout or checking system resources."
            )
            command = (
                command or "playwrightauthor status -v  # Verbose mode for details"
            )

        else:
            suggestion = suggestion or (
                "Failed to connect to Chrome. Run diagnostics to check the browser status "
                "and ensure no firewall is blocking local connections."
            )
            command = command or "playwrightauthor diagnose"

        super().__init__(
            message,
            suggestion,
            command,
            did_you_mean,
            help_link="https://github.com/twardoch/playwrightauthor/blob/main/docs/connection-issues.md",
        )


class ProfileError(PlaywrightAuthorError):
    """
    Raised for browser profile management errors.

    Common causes:
    - Profile doesn't exist
    - Profile data corrupted
    - Permission issues accessing profile
    - Profile locked by another process
    """

    def __init__(
        self,
        message: str,
        profile_name: str = None,
        suggestion: str = None,
        command: str = None,
    ):
        if profile_name:
            if "not found" in message.lower() or "does not exist" in message.lower():
                suggestion = suggestion or (
                    f"Profile '{profile_name}' doesn't exist. Create it first or use an existing profile."
                )
                command = command or f"playwrightauthor profile create {profile_name}"
                # Could add logic to suggest similar profile names

            elif "corrupt" in message.lower():
                suggestion = suggestion or (
                    f"Profile '{profile_name}' appears to be corrupted. "
                    "You may need to recreate it or restore from backup."
                )
                command = (
                    command
                    or f"playwrightauthor profile delete {profile_name} && playwrightauthor profile create {profile_name}"
                )

        else:
            suggestion = (
                suggestion
                or "Profile operation failed. Check profile name and permissions."
            )
            command = command or "playwrightauthor profile list"

        super().__init__(
            message,
            suggestion,
            command,
            help_link="https://github.com/twardoch/playwrightauthor/blob/main/docs/profiles.md",
        )


class CLIError(PlaywrightAuthorError):
    """
    Raised for CLI-specific errors.

    Common causes:
    - Invalid command syntax
    - Unknown command or option
    - Missing required arguments
    - Invalid argument values
    """

    def __init__(
        self,
        message: str,
        command_used: str = None,
        suggestion: str = None,
        command: str = None,
        did_you_mean: list[str] | None = None,
    ):
        # Auto-generate did_you_mean suggestions based on command
        if command_used and not did_you_mean:
            commands = [
                "status",
                "clear-cache",
                "profile",
                "config",
                "diagnose",
                "version",
                "repl",
            ]
            # Simple fuzzy matching
            did_you_mean = [
                cmd for cmd in commands if cmd.startswith(command_used[:3])
            ][:3]

        if not suggestion:
            suggestion = "Check command syntax and available options."

        if not command:
            command = "playwrightauthor --help  # Show all commands"

        super().__init__(
            message,
            suggestion,
            command,
            did_you_mean,
            help_link="https://github.com/twardoch/playwrightauthor#cli-reference",
        )
