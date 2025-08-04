#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["playwright"]
# ///
# this_file: src/playwrightauthor/onboarding.py

"""Enhanced onboarding with login detection and user guidance."""

import asyncio
import platform
from pathlib import Path

from playwright.async_api import Browser as AsyncBrowser
from playwright.async_api import Page


async def _detect_login_activity(page: Page, logger) -> bool:
    """
    Detect if the user has performed login activities.

    Returns True if login activity is detected, False otherwise.
    """
    try:
        # Check for common login indicators
        [
            # Common cookie names that indicate authentication
            lambda: page.context.cookies(),
            # Check for localStorage items that might indicate login
            lambda: page.evaluate("() => Object.keys(localStorage).length > 0"),
            # Check for sessionStorage items
            lambda: page.evaluate("() => Object.keys(sessionStorage).length > 0"),
        ]

        # Check cookies for authentication-related names
        cookies = await page.context.cookies()
        auth_cookie_patterns = [
            "session",
            "auth",
            "token",
            "login",
            "user",
            "jwt",
            "access_token",
            "sid",
            "sessionid",
            "PHPSESSID",
            "connect.sid",
            "_session",
            "laravel_session",
        ]

        auth_cookies = [
            cookie
            for cookie in cookies
            if any(
                pattern.lower() in cookie["name"].lower()
                for pattern in auth_cookie_patterns
            )
        ]

        if auth_cookies:
            logger.info(f"Detected {len(auth_cookies)} authentication-related cookies")
            return True

        # Check for local/session storage (indicates interaction with web apps)
        try:
            local_storage_count = await page.evaluate(
                "() => Object.keys(localStorage).length"
            )
            session_storage_count = await page.evaluate(
                "() => Object.keys(sessionStorage).length"
            )

            if local_storage_count > 0 or session_storage_count > 0:
                logger.info(
                    f"Detected browser storage activity (localStorage: {local_storage_count}, sessionStorage: {session_storage_count})"
                )
                return True
        except Exception:
            pass  # Storage might not be available on all pages

        return False

    except Exception as e:
        logger.debug(f"Error detecting login activity: {e}")
        return False


async def _wait_for_user_action(page: Page, logger, timeout: int = 300) -> str:
    """
    Wait for user to either navigate away or perform login activities.

    Returns:
        'navigation' if user navigated away
        'login_detected' if login activity was detected
        'timeout' if timeout occurred
    """
    start_time = asyncio.get_event_loop().time()
    check_interval = 5  # Check every 5 seconds

    logger.info("Monitoring for user activity...")

    try:
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            # Check if user navigated away
            if page.url != "about:blank" and not page.url.startswith("data:"):
                logger.info(f"User navigated to: {page.url}")
                return "navigation"

            # Check for login activity
            if await _detect_login_activity(page, logger):
                logger.info("Login activity detected")
                return "login_detected"

            # Wait before next check
            await asyncio.sleep(check_interval)

        logger.warning(f"Timeout after {timeout} seconds")
        return "timeout"

    except Exception as e:
        logger.error(f"Error waiting for user action: {e}")
        return "error"


async def _detect_setup_issues(page: Page, logger) -> list[dict[str, str]]:
    """
    Auto-detect common authentication and setup issues.

    Returns:
        List of issues found, each with 'type', 'description', and 'solution' keys.
    """
    issues = []

    try:
        # Check for JavaScript errors that might block authentication
        js_errors = await page.evaluate("""() => {
            const errors = [];
            const originalError = console.error;
            window.jsErrors = window.jsErrors || [];
            return window.jsErrors.slice(-10); // Get recent errors
        }""")

        if js_errors and len(js_errors) > 0:
            issues.append(
                {
                    "type": "javascript_errors",
                    "description": f"JavaScript errors detected: {len(js_errors)} recent errors",
                    "solution": "Try refreshing the page or checking browser console for details",
                }
            )
    except Exception:
        pass

    try:
        # Check if cookies are blocked
        await page.evaluate("document.cookie = 'test=value'")
        test_cookie = await page.evaluate("document.cookie.includes('test=value')")
        if not test_cookie:
            issues.append(
                {
                    "type": "cookies_blocked",
                    "description": "Cookies appear to be blocked or disabled",
                    "solution": "Enable cookies in browser settings for authentication to work",
                }
            )
    except Exception:
        issues.append(
            {
                "type": "cookie_test_failed",
                "description": "Unable to test cookie functionality",
                "solution": "Check browser permissions and try refreshing the page",
            }
        )

    try:
        # Check for popup blocker issues
        popup_blocked = await page.evaluate("""() => {
            try {
                const popup = window.open('about:blank', '_blank');
                if (popup) {
                    popup.close();
                    return false;  // Popups work
                }
                return true;  // Popup blocked
            } catch (e) {
                return true;  // Popup blocked
            }
        }""")

        if popup_blocked:
            issues.append(
                {
                    "type": "popup_blocked",
                    "description": "Popup blocker may interfere with OAuth login flows",
                    "solution": "Allow popups for this site or look for popup notification in browser",
                }
            )
    except Exception:
        pass

    try:
        # Check for third-party cookie restrictions
        third_party_blocked = await page.evaluate("""() => {
            // This is a simplified check - real detection would be more complex
            return navigator.userAgent.includes('Chrome') &&
                   window.chrome &&
                   window.chrome.runtime === undefined;
        }""")

        if third_party_blocked:
            issues.append(
                {
                    "type": "third_party_cookies",
                    "description": "Third-party cookies may be restricted",
                    "solution": "Enable third-party cookies for authentication with external services",
                }
            )
    except Exception:
        pass

    # Check for network connectivity issues
    try:
        network_test = await page.evaluate("""() => {
            return fetch('https://www.google.com/generate_204', {
                method: 'HEAD',
                mode: 'no-cors'
            }).then(() => true).catch(() => false);
        }""")

        if not network_test:
            issues.append(
                {
                    "type": "network_connectivity",
                    "description": "Network connectivity issues detected",
                    "solution": "Check internet connection and firewall settings",
                }
            )
    except Exception:
        pass

    return issues


async def _provide_service_guidance(logger) -> dict[str, str]:
    """
    Provide specific guidance for common authentication services.

    Returns:
        Dictionary mapping service names to setup instructions.
    """
    return {
        "Gmail/Google": """
            1. Go to https://accounts.google.com
            2. Click 'Sign in' and enter your credentials
            3. Enable 2FA if prompted (recommended)
            4. You may need to verify with phone/backup codes
        """,
        "GitHub": """
            1. Navigate to https://github.com/login
            2. Enter your GitHub username and password
            3. Complete 2FA if enabled (authenticator app or SMS)
            4. You'll stay logged in for future automation
        """,
        "LinkedIn": """
            1. Go to https://www.linkedin.com/login
            2. Enter your email and password
            3. Complete any security challenges if prompted
            4. Consider enabling 2FA for better security
        """,
        "Microsoft/Office 365": """
            1. Visit https://login.microsoftonline.com
            2. Enter your Microsoft account credentials
            3. Complete MFA if required (Authenticator app recommended)
            4. Accept any device registration prompts
        """,
        "Facebook": """
            1. Navigate to https://www.facebook.com
            2. Log in with your credentials
            3. Complete 2FA if enabled
            4. Approve any new device notifications
        """,
        "Twitter/X": """
            1. Go to https://twitter.com/login
            2. Enter your username/email and password
            3. Complete 2FA verification if enabled
            4. Verify device if prompted
        """,
    }


async def _check_browser_permissions(logger) -> list[dict[str, str]]:
    """
    Check for browser permission issues that might affect automation.

    Returns:
        List of permission issues found.
    """
    issues = []
    system = platform.system()

    if system == "Darwin":  # macOS
        issues.append(
            {
                "type": "macos_permissions",
                "description": "macOS may require accessibility permissions",
                "solution": "Go to System Preferences → Security & Privacy → Privacy → Accessibility and allow Terminal/Chrome",
            }
        )
    elif system == "Linux":
        # Check for display issues
        import os

        if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
            issues.append(
                {
                    "type": "linux_display",
                    "description": "No display environment detected",
                    "solution": "Set DISPLAY variable or run in headless mode",
                }
            )
    elif system == "Windows":
        issues.append(
            {
                "type": "windows_firewall",
                "description": "Windows Firewall may block browser connections",
                "solution": "Allow Chrome and Python through Windows Firewall if prompted",
            }
        )

    return issues


async def _generate_setup_report(page: Page, logger) -> dict:
    """
    Generate comprehensive setup report with issues and recommendations.

    Returns:
        Dictionary with setup status, issues, and recommendations.
    """
    logger.info("Generating setup report...")

    # Detect setup issues
    issues = await _detect_setup_issues(page, logger)

    # Check browser permissions
    permission_issues = await _check_browser_permissions(logger)
    issues.extend(permission_issues)

    # Get service guidance
    service_guidance = await _provide_service_guidance(logger)

    # Detect current page type for contextual help
    current_url = page.url
    current_service = "Unknown"
    contextual_help = ""

    if "google.com" in current_url or "gmail.com" in current_url:
        current_service = "Google/Gmail"
        contextual_help = service_guidance.get("Gmail/Google", "")
    elif "github.com" in current_url:
        current_service = "GitHub"
        contextual_help = service_guidance.get("GitHub", "")
    elif "linkedin.com" in current_url:
        current_service = "LinkedIn"
        contextual_help = service_guidance.get("LinkedIn", "")
    elif "microsoft.com" in current_url or "office.com" in current_url:
        current_service = "Microsoft"
        contextual_help = service_guidance.get("Microsoft/Office 365", "")

    report = {
        "timestamp": asyncio.get_event_loop().time(),
        "current_url": current_url,
        "current_service": current_service,
        "contextual_help": contextual_help.strip(),
        "issues_found": len(issues),
        "issues": issues,
        "all_services": service_guidance,
        "recommendations": [],
    }

    # Generate recommendations based on issues
    if len(issues) == 0:
        report["recommendations"].append(
            "✅ No issues detected - your setup looks good!"
        )
    else:
        report["recommendations"].append(
            "⚠️ Issues detected that may affect authentication:"
        )
        for issue in issues:
            report["recommendations"].append(
                f"• {issue['description']}: {issue['solution']}"
            )

    if current_service != "Unknown":
        report["recommendations"].append(
            f"💡 You're on {current_service} - follow the service-specific guidance above"
        )

    return report


async def show(browser: AsyncBrowser, logger, timeout: int = 300) -> None:
    """
    Shows the enhanced onboarding page with intelligent setup guidance.

    Args:
        browser: Playwright browser instance
        logger: Logger instance
        timeout: Maximum time to wait for user action (seconds)
    """
    html_path = Path(__file__).parent / "templates" / "onboarding.html"

    if not html_path.exists():
        logger.error(f"Onboarding template not found: {html_path}")
        return

    page = await browser.new_page()

    try:
        # Load onboarding page
        html_content = html_path.read_text("utf-8")
        await page.set_content(html_content, wait_until="domcontentloaded")
        logger.info("Enhanced onboarding page displayed")

        # Generate initial setup report
        initial_report = await _generate_setup_report(page, logger)

        if initial_report["issues_found"] > 0:
            logger.warning(
                f"Setup issues detected: {initial_report['issues_found']} issues found"
            )
            for issue in initial_report["issues"]:
                logger.warning(f"  - {issue['description']}: {issue['solution']}")
        else:
            logger.info("Initial setup check passed - no issues detected")

        # Enhanced monitoring with periodic issue checks
        start_time = asyncio.get_event_loop().time()
        check_interval = 5
        last_report_time = start_time
        report_interval = 30  # Generate detailed report every 30 seconds

        logger.info("Starting enhanced monitoring for user activity...")

        while (asyncio.get_event_loop().time() - start_time) < timeout:
            current_time = asyncio.get_event_loop().time()

            # Check if user navigated away
            if page.url != "about:blank" and not page.url.startswith("data:"):
                logger.info(f"User navigated to: {page.url}")

                # Generate contextual setup report for the new page
                navigation_report = await _generate_setup_report(page, logger)

                if navigation_report["current_service"] != "Unknown":
                    logger.info(
                        f"Detected service: {navigation_report['current_service']}"
                    )
                    if navigation_report["contextual_help"]:
                        logger.info("Service-specific guidance:")
                        for line in navigation_report["contextual_help"].split("\n"):
                            if line.strip():
                                logger.info(f"  {line.strip()}")

                if navigation_report["issues_found"] > 0:
                    logger.warning(
                        f"New issues detected on {navigation_report['current_service']}:"
                    )
                    for issue in navigation_report["issues"]:
                        logger.warning(
                            f"  - {issue['description']}: {issue['solution']}"
                        )

                # Continue monitoring for login completion
                result = await _wait_for_user_action(page, logger, timeout // 2)

                if result == "login_detected":
                    logger.info(
                        "Authentication activity detected - onboarding complete!"
                    )
                    return
                elif result == "timeout":
                    logger.info(
                        "No authentication detected, but user has navigated - onboarding considered successful"
                    )
                    return
                else:
                    logger.info("User navigation detected - onboarding complete")
                    return

            # Check for login activity
            if await _detect_login_activity(page, logger):
                logger.info("Login activity detected - onboarding complete!")
                return

            # Generate periodic detailed reports
            if (current_time - last_report_time) >= report_interval:
                periodic_report = await _generate_setup_report(page, logger)

                if periodic_report["issues_found"] > 0:
                    logger.info("Periodic setup check - issues still present:")
                    for issue in periodic_report["issues"]:
                        logger.info(f"  - {issue['description']}")
                else:
                    logger.info("Periodic setup check - all systems ready")

                last_report_time = current_time

            # Wait before next check
            await asyncio.sleep(check_interval)

        logger.warning(f"Onboarding timed out after {timeout} seconds")

        # Generate final report
        final_report = await _generate_setup_report(page, logger)
        logger.info("Final setup status:")
        for recommendation in final_report["recommendations"]:
            logger.info(f"  {recommendation}")

    except Exception as e:
        logger.error(f"Error during enhanced onboarding: {e}")
        # Generate error report to help with troubleshooting
        try:
            error_report = await _generate_setup_report(page, logger)
            logger.error("Setup status at error time:")
            for recommendation in error_report["recommendations"]:
                logger.error(f"  {recommendation}")
        except Exception:
            pass
    finally:
        try:
            if not page.is_closed():
                await page.close()
                logger.debug("Onboarding page closed")
        except Exception as e:
            logger.debug(f"Error closing onboarding page: {e}")


async def show_with_retry(
    browser: AsyncBrowser, logger, max_retries: int = 2, timeout: int = 300
) -> None:
    """
    Show onboarding with retry logic for error resilience.

    Args:
        browser: Playwright browser instance
        logger: Logger instance
        max_retries: Maximum number of retry attempts
        timeout: Timeout per attempt
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Starting onboarding attempt {attempt + 1}/{max_retries}")
            await show(browser, logger, timeout)
            return  # Success

        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"Onboarding attempt {attempt + 1} failed: {e}. Retrying..."
                )
                await asyncio.sleep(2)  # Brief delay before retry
            else:
                logger.error(f"All onboarding attempts failed. Last error: {e}")
                raise


async def interactive_setup_wizard(browser: AsyncBrowser, logger) -> bool:
    """
    Interactive setup wizard for first-time users.

    Provides step-by-step guidance and validates each step.

    Args:
        browser: Playwright browser instance
        logger: Logger instance

    Returns:
        True if setup completed successfully, False otherwise
    """
    logger.info("🎭 Starting PlaywrightAuthor Interactive Setup Wizard")
    logger.info(
        "This wizard will guide you through setting up your authenticated browser."
    )

    # Step 1: Browser Validation
    logger.info("\n📋 Step 1: Browser Validation")
    page = await browser.new_page()

    try:
        # Test basic browser functionality
        await page.goto("about:blank")
        logger.info("✅ Browser connection successful")

        # Generate initial setup report
        initial_report = await _generate_setup_report(page, logger)

        if initial_report["issues_found"] > 0:
            logger.warning(
                f"⚠️ Found {initial_report['issues_found']} potential issues:"
            )
            for issue in initial_report["issues"]:
                logger.warning(f"   • {issue['description']}")
                logger.info(f"     💡 Solution: {issue['solution']}")
        else:
            logger.info("✅ No browser issues detected")

        # Step 2: Service Selection Guidance
        logger.info("\n🌐 Step 2: Service Authentication Guidance")
        service_guidance = await _provide_service_guidance(logger)

        logger.info("Choose a service to authenticate with (or navigate manually):")
        for i, (service, instructions) in enumerate(service_guidance.items(), 1):
            logger.info(f"\n{i}. {service}")
            # Show brief instructions
            lines = instructions.strip().split("\n")
            if len(lines) > 2:
                logger.info(f"   {lines[1].strip()}")
                logger.info(f"   {lines[2].strip()}")

        logger.info("\n📝 Instructions:")
        logger.info("   • Open a new tab (Ctrl+T or Cmd+T)")
        logger.info("   • Navigate to your chosen service")
        logger.info("   • Complete the login process")
        logger.info("   • The wizard will automatically detect completion")

        # Step 3: Wait for Navigation with Enhanced Monitoring
        logger.info("\n⏳ Step 3: Waiting for User Authentication")
        logger.info(
            "Navigate to any service and log in. The wizard will monitor your progress..."
        )

        success = False
        start_time = asyncio.get_event_loop().time()
        timeout = 600  # 10 minutes for interactive setup
        check_interval = 10  # Check every 10 seconds

        while (asyncio.get_event_loop().time() - start_time) < timeout:
            # Check for navigation
            if page.url != "about:blank" and not page.url.startswith("data:"):
                logger.info(f"🌐 Navigation detected: {page.url}")

                # Generate contextual report
                navigation_report = await _generate_setup_report(page, logger)

                if navigation_report["current_service"] != "Unknown":
                    logger.info(
                        f"🎯 Detected service: {navigation_report['current_service']}"
                    )
                    if navigation_report["contextual_help"]:
                        logger.info("📋 Service-specific guidance:")
                        for line in navigation_report["contextual_help"].split("\n"):
                            if line.strip():
                                logger.info(f"   {line.strip()}")

                # Check for new issues on this page
                if navigation_report["issues_found"] > 0:
                    logger.warning("⚠️ New issues detected on this page:")
                    for issue in navigation_report["issues"]:
                        logger.warning(
                            f"   • {issue['description']}: {issue['solution']}"
                        )

                # Wait for login completion
                logger.info("⏳ Monitoring for authentication completion...")
                login_result = await _wait_for_user_action(
                    page, logger, 300
                )  # 5 minutes

                if login_result == "login_detected":
                    logger.info("🎉 Authentication detected!")
                    success = True
                    break
                elif login_result == "navigation":
                    logger.info(
                        "🌐 Additional navigation detected - continuing to monitor..."
                    )
                    continue
                else:
                    logger.info("⏰ No authentication detected within timeout")
                    break

            # Check for login activity on the current page
            if await _detect_login_activity(page, logger):
                logger.info("🎉 Login activity detected!")
                success = True
                break

            await asyncio.sleep(check_interval)

        # Step 4: Final Validation
        logger.info("\n🔍 Step 4: Final Validation")

        if success:
            # Validate that authentication was successful
            await _generate_setup_report(page, logger)

            # Check for cookies and storage indicating successful login
            login_indicators = await _detect_login_activity(page, logger)

            if login_indicators:
                logger.info("✅ Setup completed successfully!")
                logger.info("🎯 Authentication detected and validated")
                logger.info("🚀 Your browser is now ready for automation!")

                logger.info("\n📚 Next Steps:")
                logger.info("   • Your login sessions are now saved")
                logger.info("   • You can start using PlaywrightAuthor in your scripts")
                logger.info(
                    "   • Use 'playwrightauthor status' to check browser status"
                )
                logger.info(
                    "   • Use 'playwrightauthor health' for comprehensive diagnostics"
                )

                return True
            else:
                logger.warning(
                    "⚠️ Setup completed, but authentication validation unclear"
                )
                logger.info("💡 You may need to log in again when using automation")
                return True
        else:
            logger.warning("⏰ Setup wizard timed out")
            logger.info("💡 You can:")
            logger.info("   • Run the wizard again: playwrightauthor setup")
            logger.info(
                "   • Use the browser manually and authentication will be detected"
            )
            logger.info("   • Check for issues: playwrightauthor health")
            return False

    except Exception as e:
        logger.error(f"❌ Setup wizard encountered an error: {e}")

        # Provide error-specific guidance
        try:
            error_report = await _generate_setup_report(page, logger)
            logger.error("🔍 Error diagnosis:")
            for recommendation in error_report["recommendations"]:
                logger.error(f"   {recommendation}")
        except Exception:
            pass

        logger.info("\n🛠️ Troubleshooting:")
        logger.info("   • Try: playwrightauthor clear-cache")
        logger.info("   • Check: playwrightauthor health --verbose")
        logger.info("   • Review: Browser permissions and firewall settings")

        return False

    finally:
        try:
            if not page.is_closed():
                await page.close()
        except Exception:
            pass


def get_setup_recommendations() -> list[str]:
    """
    Get platform-specific setup recommendations for first-time users.

    Returns:
        List of setup recommendations as strings.
    """
    recommendations = [
        "🎭 PlaywrightAuthor Setup Recommendations",
        "",
        "📋 Before You Start:",
        "• Ensure you have a stable internet connection",
        "• Close any existing Chrome browser windows",
        "• Have your login credentials ready for services you want to automate",
        "",
        "🔐 Authentication Best Practices:",
        "• Enable 2FA where possible for better security",
        "• Use app-specific passwords for Google/Microsoft if required",
        "• Keep backup codes accessible for 2FA recovery",
        "",
    ]

    system = platform.system()

    if system == "Darwin":  # macOS
        recommendations.extend(
            [
                "🍎 macOS-Specific Setup:",
                "• Grant accessibility permissions to Terminal/ITerm when prompted",
                "• Allow Chrome through macOS security warnings",
                "• Consider disabling SIP restrictions if you encounter issues",
                "",
            ]
        )
    elif system == "Linux":
        recommendations.extend(
            [
                "🐧 Linux-Specific Setup:",
                "• Ensure DISPLAY variable is set for GUI applications",
                "• Install Chrome dependencies: sudo apt-get install -y fonts-liberation libasound2",
                "• For headless servers, consider running in headless mode",
                "",
            ]
        )
    elif system == "Windows":
        recommendations.extend(
            [
                "🪟 Windows-Specific Setup:",
                "• Allow Chrome and Python through Windows Firewall when prompted",
                "• Run as Administrator if you encounter permission issues",
                "• Disable antivirus real-time scanning temporarily if needed",
                "",
            ]
        )

    recommendations.extend(
        [
            "🌐 Common Services Setup:",
            "• Google: Visit accounts.google.com and complete 2FA setup",
            "• GitHub: Use github.com/login and consider personal access tokens",
            "• LinkedIn: Use linkedin.com/login and enable 2FA for security",
            "• Microsoft: Visit login.microsoftonline.com for Office 365",
            "",
            "🆘 If You Need Help:",
            "• Run: playwrightauthor health --verbose",
            "• Check: Browser console for JavaScript errors",
            "• Try: playwrightauthor clear-cache if issues persist",
            "• Review: Network connectivity and proxy settings",
        ]
    )

    return recommendations
