#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["playwright"]
# ///
# this_file: playwrightauthor/onboarding.py

"""Serve a local HTML page instructing the user to log in."""

from pathlib import Path
from playwright.async_api import Browser as AsyncBrowser


async def show(browser: AsyncBrowser, logger) -> None:
    """Shows the onboarding page in a new tab and waits for the user to navigate away."""
    html_path = Path(__file__).parent / "templates" / "onboarding.html"
    page = await browser.new_page()
    await page.set_content(html_path.read_text("utf-8"), wait_until="domcontentloaded")
    logger.info("Onboarding page shown. Waiting for user to navigate to a different page...")
    try:
        await page.wait_for_navigation(timeout=300_000)  # 5 minutes
        logger.info("User navigated away from the onboarding page.")
    except Exception:
        logger.warning("Timed out waiting for user to navigate away from the onboarding page.")
    finally:
        await page.close()
