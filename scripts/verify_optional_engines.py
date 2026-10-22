#!/usr/bin/env -S uv run --no-sync
# this_file: scripts/verify_optional_engines.py
"""Verify optional native sessions against an intercepted fixture, never a provider."""

import asyncio
import json
import platform
import tempfile
import time
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

import fire

from playwrightauthor import AsyncBrowserSession, BrowserSession

CHARACTERISTICS = "()=>({ua:navigator.userAgent,cores:navigator.hardwareConcurrency,screen:[screen.width,screen.height]})"
URL = "https://example.com/"


async def restart(engine: str, root: Path, expected: dict) -> str:
    async with AsyncBrowserSession(
        engine=engine, profile="optional-smoke", profile_root=root
    ) as session:
        page = await session.new_page()
        await page.route(
            URL, lambda route: route.fulfill(body="<title>fixture</title>")
        )
        await page.goto(URL)
        assert any(
            cookie["name"] == "fixture" for cookie in await session.context.cookies()
        ), "Persistent cookie lost on restart"
        assert await page.evaluate(CHARACTERISTICS) == expected, (
            "Device characteristics changed on restart"
        )
        assert await page.title() == "fixture"
        return session.browser.version if session.browser else "unknown"


def verify(
    engines: str = "cloak,camoufox", output: str = "issues/340-optional-engines.json"
) -> dict:
    results = []
    with tempfile.TemporaryDirectory(prefix="pa340-optional-") as temporary:
        root = Path(temporary)
        for engine in engines.split(","):
            if engine not in {"cloak", "camoufox"}:
                raise ValueError("Select cloak and/or camoufox")
            with BrowserSession(
                engine=engine, profile="optional-smoke", profile_root=root
            ) as session:
                page = session.new_page()
                page.route(
                    URL, lambda route: route.fulfill(body="<title>fixture</title>")
                )
                page.goto(URL)
                session.context.add_cookies(
                    [
                        {
                            "name": "fixture",
                            "value": "test",
                            "url": URL,
                            "expires": int(time.time()) + 3600,
                        }
                    ]
                )
                expected = page.evaluate(CHARACTERISTICS)
            browser_version = asyncio.run(restart(engine, root, expected))
            results.append(
                {
                    "engine": engine,
                    "package": version(
                        "cloakbrowser" if engine == "cloak" else "camoufox"
                    ),
                    "browser": browser_version,
                    "sync_to_async_restart_cookie_persistence": True,
                    "sampled_device_characteristics_stable": True,
                }
            )
    result = {
        "checked_at": datetime.now(UTC).isoformat(),
        "platform": platform.system() + " " + platform.machine(),
        "playwright": version("playwright"),
        "engines": results,
        "scope": "headless real native sessions with intercepted example.com fixture",
        "not_verified": [
            "provider authorization",
            "interactive device stability",
            "other hardware",
        ],
    }
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    fire.Fire(verify)
