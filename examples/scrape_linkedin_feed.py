#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["playwrightauthor"]
# ///
# this_file: examples/scrape_linkedin_feed.py
"""
Scrape LinkedIn feed headlines using PlaywrightAuthor.

This example demonstrates how to:
1. Use PlaywrightAuthor to access an authenticated LinkedIn session
2. Navigate to the LinkedIn feed
3. Extract post headlines and author information
4. Handle infinite scroll to load more posts

Prerequisites:
- Install PlaywrightAuthor: pip install playwrightauthor
- Run once and log into LinkedIn when the browser opens
"""

import time

from playwrightauthor import Browser


def scrape_linkedin_feed(max_posts=10):
    """Scrape recent posts from LinkedIn feed."""
    print("🔍 Starting LinkedIn feed scraper...")

    with Browser() as browser:
        # Get a page (reuses existing context with logged-in sessions)
        page = browser.get_page()

        # Navigate to LinkedIn feed
        print("📍 Navigating to LinkedIn...")
        page.goto("https://www.linkedin.com/feed/")

        # Check if we're logged in by looking for login elements
        try:
            # Check for various signs we're not logged in
            page.wait_for_selector(
                "input[name='session_key'], .sign-in-form, a[href*='/login']",
                timeout=3000,
            )
            print("❌ Not logged in to LinkedIn!")
            print("\n📝 To use this scraper:")
            print("1. Keep Chrome running with: playwrightauthor browse")
            print("2. Log into LinkedIn in the browser window")
            print("3. Run this script again")
            print("\nYour login session will be preserved in the browser.")
            return
        except:
            # Good - no login elements found, we should be logged in
            pass

        # Wait for feed to load
        print("⏳ Waiting for feed to load...")

        # Wait for the page to be ready
        try:
            # LinkedIn feed might already be loaded if we're reusing a page
            page.wait_for_load_state("domcontentloaded")
            # Give the feed a moment to populate
            page.wait_for_timeout(2000)

            # Try multiple selectors for posts
            post_selectors = [
                ".feed-shared-update-v2",
                "[data-id*='urn:li:activity']",
                "div[data-urn*='urn:li:activity']",
                ".occludable-update",
                "article.relative",
            ]

            found_selector = None
            for selector in post_selectors:
                if page.locator(selector).count() > 0:
                    found_selector = selector
                    print(f"✓ Found LinkedIn feed using selector: {selector}")
                    break

            if not found_selector:
                print("❌ Could not find LinkedIn feed posts.")
                print(f"Current URL: {page.url}")
                print("\nTrying to debug page structure...")
                # Take a screenshot for debugging
                page.screenshot(path="linkedin_debug.png")
                print("Screenshot saved as linkedin_debug.png")
                return

        except Exception as e:
            print(f"❌ Error waiting for feed: {e}")
            print(f"Current URL: {page.url}")
            return

        posts = []
        seen_posts = set()

        print(f"\n📰 Scrolling to load posts (target: {max_posts})...\n")

        while len(posts) < max_posts:
            # Get all visible posts using the found selector
            post_elements = page.locator(found_selector).all()
            print(f"Found {len(post_elements)} post elements")

            for post in post_elements:
                if len(posts) >= max_posts:
                    break

                try:
                    # Generate a unique ID for the post to avoid duplicates
                    post_id = post.get_attribute("data-urn")
                    if post_id in seen_posts:
                        continue
                    seen_posts.add(post_id)

                    # Extract author name
                    author_element = post.locator(".feed-shared-actor__name").first
                    author = (
                        author_element.inner_text()
                        if author_element.count() > 0
                        else "Unknown"
                    )

                    # Extract post text (headline)
                    text_element = post.locator(".feed-shared-text").first
                    text = ""
                    if text_element.count() > 0:
                        text = text_element.inner_text()
                        # Get first line as headline
                        text = text.split("\n")[0] if "\n" in text else text
                        text = text[:100] + "..." if len(text) > 100 else text

                    # Extract post time
                    time_element = post.locator(
                        ".feed-shared-actor__sub-description"
                    ).first
                    post_time = (
                        time_element.inner_text() if time_element.count() > 0 else ""
                    )

                    if text:  # Only add posts with text content
                        posts.append(
                            {
                                "author": author.strip(),
                                "headline": text.strip(),
                                "time": post_time.strip(),
                            }
                        )

                        print(f"  👤 {author}")
                        print(f"  📝 {text}")
                        print(f"  🕒 {post_time}\n")

                except Exception:
                    # Skip problematic posts
                    continue

            # Scroll down to load more posts
            if len(posts) < max_posts:
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                time.sleep(2)  # Wait for new posts to load

                # Check if we're stuck (no new posts loading)
                new_post_count = len(page.locator(found_selector).all())
                if new_post_count == len(post_elements):
                    print("⚠️  No more posts to load")
                    break

        print(f"\n✅ Successfully scraped {len(posts)} posts from LinkedIn feed!")
        return posts


if __name__ == "__main__":
    try:
        # Scrape 10 recent posts from LinkedIn feed
        posts = scrape_linkedin_feed(max_posts=10)

        if posts:
            print("\n📊 Summary:")
            print(f"Total posts scraped: {len(posts)}")

            # Show unique authors
            authors = {post["author"] for post in posts}
            print(f"Unique authors: {len(authors)}")

    except KeyboardInterrupt:
        print("\n\n👋 Scraping cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Try running with Browser(verbose=True) for more details.")
