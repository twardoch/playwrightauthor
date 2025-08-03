#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["playwright>=1.43.0", "loguru>=0.7.0", "rich>=13.0.0", "fire>=0.5.0", "requests>=2.31.0"]
# ///
# this_file: old/google_docs_scraper_simple.py

"""
Google Docs Browser Automation Scraper (Simple Version)

Just connects to existing Chrome and uses existing tabs where you're already logged in.
"""

import asyncio

import fire
from loguru import logger
from playwright.async_api import async_playwright
from rich.console import Console
from rich.pretty import pprint


async def scrape_google_docs(
    debug_port: int = 9222, verbose: bool = False
) -> list[str]:
    """Connect to existing Chrome and scrape Google Docs titles from existing tabs."""

    if verbose:
        logger.add(lambda msg: print(msg), level="DEBUG")

    console = Console()
    console.print("[blue]Connecting to existing Chrome...[/blue]")

    async with async_playwright() as p:
        # Connect to existing Chrome
        browser = await p.chromium.connect_over_cdp(f"http://localhost:{debug_port}")

        # Get existing contexts and pages
        contexts = browser.contexts
        if not contexts:
            console.print("[red]No contexts found in browser[/red]")
            return []

        # Look through all existing pages for Google Docs
        all_titles = []
        page_to_use = None

        # First, try to find a suitable existing page
        for context in contexts:
            pages = context.pages
            console.print(f"[dim]Found {len(pages)} pages in context[/dim]")

            for page in pages:
                url = page.url
                console.print(f"[dim]Checking page: {url[:80]}...[/dim]")

                # Use any page that's not an extension or chrome:// page
                if not url.startswith("chrome-extension://") and not url.startswith(
                    "chrome://"
                ):
                    page_to_use = page
                    break

            if page_to_use:
                break

        # If no suitable page found, create a new one
        if not page_to_use:
            console.print("[yellow]No suitable page found, creating new one[/yellow]")
            context = contexts[0]
            page_to_use = await context.new_page()

        console.print("[green]Navigating to Google Docs...[/green]")
        await page_to_use.goto(
            "https://docs.google.com/document/", wait_until="domcontentloaded"
        )
        await asyncio.sleep(2)

        # Try to find document titles
        selectors = [
            "div.docs-homescreen-list-item-title-value",
            "[data-id] .docs-homescreen-list-item-title-value",
            ".docs-homescreen-list-item-title",
        ]

        for selector in selectors:
            try:
                elements = await page_to_use.query_selector_all(selector)
                if elements:
                    console.print(
                        f"[green]Found {len(elements)} documents with selector: {selector}[/green]"
                    )

                    for element in elements:
                        text = await element.text_content()
                        if text and text.strip():
                            all_titles.append(text.strip())
                    break
            except Exception:
                continue

        await browser.close()

        # Remove duplicates
        unique_titles = list(dict.fromkeys(all_titles))
        return unique_titles


def main(debug_port: int = 9222, verbose: bool = False) -> None:
    """
    Scrape Google Docs titles using existing Chrome tabs.

    Make sure you have Chrome running with:
    --remote-debugging-port=9222

    And you have a tab open with Google Docs where you're logged in.
    """
    console = Console()

    try:
        titles = asyncio.run(scrape_google_docs(debug_port, verbose))

        if titles:
            console.print(f"\n[green]Found {len(titles)} documents:[/green]")
            pprint(titles, console=console)
        else:
            console.print(
                "[yellow]No documents found. Make sure you have Google Docs open in a tab.[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    fire.Fire(main)
