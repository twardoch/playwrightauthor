# this_file: tests/test_author.py
import pytest

from playwrightauthor import AsyncBrowser, Browser


def test_browser_notifies_interactive_task(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_notify_interactive_task(**kwargs: object) -> bool:
        calls.append(kwargs)
        return True

    monkeypatch.setattr(
        "playwrightauthor.author.notify_interactive_task",
        fake_notify_interactive_task,
    )

    browser = Browser(
        profile="google-primary",
        service="Gemini",
        task="Sign in if prompted.",
        suppress_dialog=True,
    )
    browser._notify_interactive_task()

    assert calls == [
        {
            "task": "Sign in if prompted.",
            "profile": "google-primary",
            "service": "Gemini",
            "suppress": True,
        }
    ]


@pytest.mark.skip(
    reason="This is an integration test that requires a live Chrome instance and potentially user interaction."
)
def test_browser_smoke():
    """A basic smoke test to ensure the Browser class can be instantiated."""
    try:
        with Browser(verbose=True) as browser:
            assert browser is not None
            page = browser.new_page()
            page.goto("https://www.google.com")
            assert "Google" in page.title()
            page.close()
    except Exception as e:
        pytest.fail(f"Browser smoke test failed with an exception: {e}")


@pytest.mark.skip(
    reason="This is an integration test that requires a live Chrome instance and potentially user interaction."
)
@pytest.mark.asyncio
async def test_async_browser_smoke():
    """A basic smoke test to ensure the AsyncBrowser class can be instantiated."""
    try:
        async with AsyncBrowser(verbose=True) as browser:
            assert browser is not None
            page = await browser.new_page()
            await page.goto("https://www.duckduckgo.com")
            title = await page.title()
            assert "DuckDuckGo" in title
            await page.close()
    except Exception as e:
        pytest.fail(f"AsyncBrowser smoke test failed with an exception: {e}")
