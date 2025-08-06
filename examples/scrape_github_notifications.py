#!/usr/bin/env python3
# this_file: examples/scrape_github_notifications.py
"""
Scrape GitHub notifications using PlaywrightAuthor.

This example demonstrates how to:
1. Use PlaywrightAuthor to access an authenticated GitHub session
2. Navigate to the notifications page
3. Extract notification titles and repository names
4. Handle cases where login is required

Prerequisites:
- Install PlaywrightAuthor: pip install playwrightauthor
- Run once and log into GitHub when the browser opens
"""

from playwrightauthor import Browser


def scrape_github_notifications():
    """Scrape notification titles from GitHub."""
    print("🔍 Starting GitHub notifications scraper...")

    with Browser() as browser:
        # Get a page (reuses existing context with logged-in sessions)
        page = browser.get_page()

        # Navigate to GitHub notifications
        print("📍 Navigating to GitHub notifications...")
        page.goto("https://github.com/notifications")

        # Check if we're logged in by looking for the notifications UI
        if page.locator("a[href='/login']").count() > 0:
            print("❌ Not logged in to GitHub!")
            print("👉 Please run the script again and log in when the browser opens.")
            print("   Your login session will be saved for future runs.")
            return

        # Wait for notifications to load
        page.wait_for_load_state("networkidle")

        # Extract notifications
        notifications = []

        # GitHub notifications are in a specific structure
        notification_items = page.locator(".Box-row.Box-row--hover-gray").all()

        if not notification_items:
            print("📭 No notifications found!")
            return

        print(f"\n📬 Found {len(notification_items)} notifications:\n")

        for item in notification_items:
            try:
                # Extract notification title
                title_element = item.locator(".markdown-title")
                title = (
                    title_element.inner_text()
                    if title_element.count() > 0
                    else "No title"
                )

                # Extract repository name
                repo_element = item.locator("a.Link--muted").first
                repo = (
                    repo_element.inner_text()
                    if repo_element.count() > 0
                    else "Unknown repo"
                )

                # Extract notification type (issue, PR, etc.)
                # Note: Type detection could be enhanced by analyzing SVG icons
                notification_type = "Notification"  # Default

                notifications.append(
                    {
                        "title": title.strip(),
                        "repo": repo.strip(),
                        "type": notification_type,
                    }
                )

                print(f"  📌 [{repo}] {title}")

            except Exception as e:
                print(f"  ⚠️  Error parsing notification: {e}")

        print(f"\n✅ Successfully scraped {len(notifications)} notifications!")
        return notifications


if __name__ == "__main__":
    try:
        scrape_github_notifications()
    except KeyboardInterrupt:
        print("\n\n👋 Scraping cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Try running with Browser(verbose=True) for more details.")
