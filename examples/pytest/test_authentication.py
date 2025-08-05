#!/usr/bin/env python3
# examples/pytest/test_authentication.py

"""
Authentication testing patterns with PlaywrightAuthor.

This module demonstrates testing login flows, session persistence,
and authenticated user scenarios using browser automation.
"""

import pytest
from playwright.sync_api import expect


@pytest.mark.auth
def test_github_login_form_exists(browser, test_urls):
    """
    Test that GitHub login form is accessible and has expected elements.

    This is a safe authentication test that only verifies the login form
    exists without actually attempting to log in.
    """
    page = browser.new_page()
    page.goto(test_urls["github_login"])

    # Verify we're on the login page
    assert "login" in page.url.lower()

    # Check for login form elements
    username_field = page.locator('input[name="login"]')
    password_field = page.locator('input[name="password"]')
    login_button = page.locator('input[type="submit"][value="Sign in"]')

    expect(username_field).to_be_visible()
    expect(password_field).to_be_visible()
    expect(login_button).to_be_visible()

    # Verify form attributes
    assert username_field.get_attribute("type") in ["text", "email"]
    assert password_field.get_attribute("type") == "password"

    page.close()


@pytest.mark.auth
def test_authentication_persistence_check(browser):
    """
    Test checking for existing authentication state.

    Demonstrates how to detect if a user is already logged in
    to avoid unnecessary login attempts in test automation.
    """
    page = browser.new_page()

    # Navigate to GitHub to check authentication state
    page.goto("https://github.com")

    # Look for indicators of logged-in state
    # These selectors may change as GitHub evolves
    user_menu = page.locator('[data-target="user-menu.toggle"]').first
    login_link = page.locator('a[href="/login"]').first

    if user_menu.is_visible():
        print("✓ User appears to be logged in to GitHub")
        # Could extract username or other profile info
        # user_info = user_menu.get_attribute("aria-label")
    elif login_link.is_visible():
        print("ℹ User is not logged in to GitHub")
    else:
        print("⚠ Cannot determine authentication state")

    page.close()


@pytest.mark.auth
def test_cookie_based_authentication_check(browser):
    """
    Test authentication state detection using cookies.

    Demonstrates checking for authentication cookies that indicate
    a user session is active.
    """
    page = browser.new_page()
    page.goto("https://github.com")

    # Get all cookies for the domain
    cookies = page.context.cookies("https://github.com")

    # Look for authentication-related cookies
    auth_cookies = [
        cookie
        for cookie in cookies
        if any(
            auth_indicator in cookie["name"].lower()
            for auth_indicator in ["session", "auth", "login", "user"]
        )
    ]

    if auth_cookies:
        print(f"✓ Found {len(auth_cookies)} potential authentication cookies")
        for cookie in auth_cookies:
            print(f"  - {cookie['name']}: {len(cookie['value'])} chars")
    else:
        print("ℹ No authentication cookies found")

    # Test localStorage for auth tokens (common in SPAs)
    auth_tokens = page.evaluate("""
        () => {
            const tokens = {};
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key && (key.includes('token') || key.includes('auth') || key.includes('session'))) {
                    tokens[key] = localStorage.getItem(key).substring(0, 20) + '...';
                }
            }
            return tokens;
        }
    """)

    if auth_tokens:
        print("✓ Found authentication tokens in localStorage:")
        for key, value in auth_tokens.items():
            print(f"  - {key}: {value}")

    page.close()


@pytest.mark.auth
@pytest.mark.slow
def test_manual_authentication_guidance(browser):
    """
    Test that provides guidance for manual authentication setup.

    This test helps set up authentication state that can be reused
    in subsequent test runs through PlaywrightAuthor's profile persistence.
    """
    page = browser.new_page()

    # Navigate to login page
    page.goto("https://github.com/login")

    print("\n" + "=" * 60)
    print("MANUAL AUTHENTICATION SETUP GUIDANCE")
    print("=" * 60)
    print("1. A browser window should have opened")
    print("2. Complete the login process manually in that browser")
    print("3. Once logged in, the authentication state will be saved")
    print("4. Future tests using the same profile will be pre-authenticated")
    print("=" * 60)

    # Wait for user to potentially log in manually
    # In a real test suite, you might skip this or use environment variables
    import time

    print("Waiting 30 seconds for manual authentication (or press Ctrl+C to skip)...")
    try:
        time.sleep(30)
    except KeyboardInterrupt:
        print("\nSkipping manual authentication setup")

    # Check if authentication was completed
    current_url = page.url
    if "login" not in current_url:
        print("✓ Authentication appears successful!")
        print(f"  Current URL: {current_url}")
    else:
        print("ℹ Still on login page - authentication may not be complete")

    page.close()


@pytest.mark.auth
def test_authentication_required_endpoints(browser):
    """
    Test accessing endpoints that require authentication.

    Demonstrates handling authentication-required scenarios and
    appropriate error handling when not authenticated.
    """
    page = browser.new_page()

    # Try to access user settings (requires auth)
    page.goto("https://github.com/settings/profile")

    current_url = page.url

    if "login" in current_url:
        print("ℹ Redirected to login - authentication required")
        # Verify login form is present
        expect(page.locator('input[name="login"]')).to_be_visible()
    elif "settings" in current_url:
        print("✓ Successfully accessed authenticated endpoint")
        # Verify we can see settings content
        expect(page.locator("h1")).to_contain_text("Public profile")
    else:
        print(f"⚠ Unexpected redirect: {current_url}")

    page.close()


@pytest.mark.auth
def test_logout_functionality(browser):
    """
    Test logout functionality and session cleanup.

    Demonstrates testing logout flows and verifying that
    authentication state is properly cleared.
    """
    page = browser.new_page()
    page.goto("https://github.com")

    # Check if we're logged in first
    user_menu = page.locator('[data-target="user-menu.toggle"]').first

    if not user_menu.is_visible():
        print("ℹ User is not logged in - skipping logout test")
        page.close()
        return

    print("✓ User appears to be logged in - testing logout")

    # Click user menu to reveal logout option
    user_menu.click()

    # Look for logout/sign out link
    logout_link = page.locator('text="Sign out"').first

    if logout_link.is_visible():
        # Store some authentication state before logout
        cookies_before = len(page.context.cookies("https://github.com"))

        # Perform logout
        logout_link.click()

        # Wait for redirect to complete
        page.wait_for_load_state("networkidle")

        # Verify logout was successful
        login_link = page.locator('a[href="/login"]').first
        expect(login_link).to_be_visible()

        # Check that auth cookies were cleared
        cookies_after = len(page.context.cookies("https://github.com"))
        print(f"Cookies before logout: {cookies_before}")
        print(f"Cookies after logout: {cookies_after}")

        print("✓ Logout completed successfully")
    else:
        print("⚠ Could not find logout link")

    page.close()


@pytest.mark.auth
def test_session_timeout_handling(browser):
    """
    Test handling of session timeouts and expired authentication.

    Demonstrates patterns for dealing with authentication that
    expires during test execution.
    """
    page = browser.new_page()

    # This is a demonstration of timeout handling patterns
    # In real scenarios, you might:
    # 1. Store initial authentication timestamp
    # 2. Check for session expiry indicators
    # 3. Re-authenticate if needed

    page.goto("https://github.com")

    # Simulate checking for session expiry indicators
    # These would be specific to your application
    session_expired_indicators = [
        'text="Session expired"',
        'text="Please log in again"',
        '[data-test="session-expired"]',
    ]

    session_expired = False
    for indicator in session_expired_indicators:
        if page.locator(indicator).is_visible():
            session_expired = True
            print(f"✓ Detected session expiry: {indicator}")
            break

    if not session_expired:
        print("ℹ No session expiry detected")

    # In a real implementation, you might:
    # if session_expired:
    #     perform_re_authentication(page)

    page.close()


@pytest.mark.auth
def test_multi_factor_authentication_detection(browser):
    """
    Test detection of multi-factor authentication requirements.

    Demonstrates handling 2FA/MFA flows that may interrupt
    automated login processes.
    """
    page = browser.new_page()
    page.goto("https://github.com/login")

    # MFA indicators that might appear during login
    mfa_indicators = [
        '[placeholder*="authentication code"]',
        'text="Two-factor authentication"',
        'text="Verify your identity"',
        '[data-test="mfa-prompt"]',
        'input[name="otp"]',
    ]

    print("Checking for MFA indicators...")

    mfa_detected = False
    for indicator in mfa_indicators:
        if page.locator(indicator).is_visible():
            mfa_detected = True
            print(f"✓ MFA indicator detected: {indicator}")

    if not mfa_detected:
        print("ℹ No MFA indicators found on login page")

    # In automated testing, you might:
    # 1. Use test accounts without MFA enabled
    # 2. Use backup codes for automation
    # 3. Skip tests that require MFA
    # 4. Use OAuth apps with specific permissions

    page.close()


@pytest.mark.auth
def test_authentication_state_preservation(profile_browser):
    """
    Test that authentication state is preserved across browser sessions.

    Demonstrates PlaywrightAuthor's profile persistence capabilities
    for maintaining login state between test runs.
    """
    # First session - check initial state
    with profile_browser("auth-persistence-test") as browser1:
        page1 = browser1.new_page()
        page1.goto("https://github.com")

        # Check authentication state
        initial_auth_state = page1.locator(
            '[data-target="user-menu.toggle"]'
        ).first.is_visible()
        print(f"Initial authentication state: {initial_auth_state}")

        page1.close()

    # Second session - verify state persistence
    with profile_browser("auth-persistence-test") as browser2:
        page2 = browser2.new_page()
        page2.goto("https://github.com")

        # Check if authentication persisted
        persistent_auth_state = page2.locator(
            '[data-target="user-menu.toggle"]'
        ).first.is_visible()
        print(f"Persistent authentication state: {persistent_auth_state}")

        # In a profile-based system, auth state should persist
        # (though this depends on the specific site's session management)

        page2.close()

    print("✓ Authentication state preservation test completed")
