#!/usr/bin/env -S uv run --quiet
# /// script
# dependencies = ["playwrightauthor", "fire", "loguru"]
# ///
# this_file: examples/google_flow.py
"""
Generate images in Google Labs "Flow" from the command line, via PlaywrightAuthor.

It opens an authenticated Flow project, drives the controls inside the prompt
box (model, aspect ratio, output count), types your prompt, submits, waits for
the result(s), and downloads each new image to disk.

Usage:
    # Simplest: just a prompt (reuses the project's current settings)
    ./google_flow.py --project_url URL --prompt "a red bicycle in the rain"

    # Drive the in-box parameters too:
    ./google_flow.py --project_url URL --prompt "..." \\
        --aspect 1:1 --count 4 --model "Nano Banana 2" --out ./shots

Prerequisites:
- Run once and log into your Google account when the browser opens; the
  PlaywrightAuthor profile reuses that session afterwards.

UI notes (verified against the live page):
- The prompt field is a Slate editor (`div[role="textbox"][contenteditable]`),
  not an <input>; we click + type rather than `fill()`.
- The model / aspect / count live in one settings popover opened by the toolbar
  button labelled like "🍌 Nano Banana 2 crop_16_9 x2". Inside it, aspect ratios
  ("16:9", "4:3", "1:1", "3:4", "9:16") and counts ("1x", "x2", "x3", "x4") are
  `role="tab"` items; the model is a nested dropdown.
- The submit button holds the `arrow_forward` icon and is `aria-disabled` until
  a non-empty prompt exists.
- Generated images are `img[src*="media.getMediaUrlRedirect"]` (same-origin,
  302-redirecting to a signed `flow-content.google` CDN JPEG). Fetching that URL
  with the browser's request context returns the raw bytes.
"""

import re
from pathlib import Path
from urllib.parse import urljoin

import fire
from loguru import logger

from playwrightauthor import Browser

# count -> the tab label Flow uses (note the inconsistent "1x" vs "x2").
_COUNT_LABEL = {1: "1x", 2: "x2", 3: "x3", 4: "x4"}
_ASPECTS = {"16:9", "4:3", "1:1", "3:4", "9:16"}


def _settings_button(page):
    """The toolbar button that opens the in-box settings popover.

    Its text carries the crop-icon ligature (e.g. "crop_16_9"), which is stable
    regardless of the selected model or count.
    """
    return page.get_by_role("button").filter(has_text=re.compile(r"crop_\d")).first


def _open_settings(page):
    """Open the in-box settings popover and return its menu locator."""
    _settings_button(page).click()
    menu = page.get_by_role("menu")
    menu.wait_for(state="visible", timeout=5_000)
    return menu


def _close_settings(page) -> None:
    """Dismiss the popover so it stops intercepting clicks on the prompt box."""
    popper = page.locator("[data-radix-popper-content-wrapper]")
    for _ in range(4):
        if popper.count() == 0:
            return
        page.keyboard.press("Escape")  # closes a nested model dropdown first
        page.wait_for_timeout(150)
        if popper.count() == 0:
            return
        # Outside-click via the toggle button reliably closes the main popover.
        _settings_button(page).click()
        page.wait_for_timeout(150)


def _select_tab(menu, name: str) -> bool:
    """Click a role=tab inside the menu whose accessible name contains `name`."""
    tab = menu.get_by_role("tab", name=name)
    if tab.count() == 0:
        return False
    tab.first.click()
    return True


def _apply_parameters(page, model, aspect, count) -> None:
    """Drive the model / aspect / count controls inside the prompt box."""
    if not any([model, aspect, count]):
        return

    menu = _open_settings(page)

    if aspect:
        if aspect not in _ASPECTS:
            logger.warning(
                f"Unknown aspect {aspect!r}; expected one of {sorted(_ASPECTS)}"
            )
        elif _select_tab(menu, aspect):
            logger.info(f"Aspect set to {aspect}")
        else:
            logger.warning(f"Could not find aspect tab {aspect!r}")

    if count:
        label = _COUNT_LABEL.get(count)
        if not label:
            logger.warning(f"Unsupported count {count!r}; expected 1-4")
        elif _select_tab(menu, label):
            logger.info(f"Output count set to {count}")
        else:
            logger.warning(f"Could not find count tab {label!r}")

    if model:
        # The model is a nested dropdown inside the popover.
        dropdown = menu.get_by_role("button").filter(has_text="arrow_drop_down")
        if dropdown.count():
            dropdown.first.click()
            option = page.get_by_role("menuitem", name=model)
            if option.count():
                option.first.click()
                logger.info(f"Model set to {model}")
            else:
                logger.warning(f"Model {model!r} not offered; leaving current model")

    # Close the popover so it doesn't intercept the prompt click.
    _close_settings(page)


def generate(
    project_url: str,
    prompt: str,
    model: str | None = None,
    aspect: str | None = None,
    count: int | None = None,
    out: str = "flow_output",
    timeout: int = 180,
    verbose: bool = False,
) -> list[str]:
    """Generate image(s) in a Flow project and download them.

    Args:
        project_url: Full Flow project URL.
        prompt: Text prompt to type into the prompt box.
        model: Optional model name to select (e.g. "Nano Banana 2").
        aspect: Optional aspect ratio: 16:9, 4:3, 1:1, 3:4, or 9:16.
        count: Optional number of images to request (1-4).
        out: Directory to save downloaded JPEGs into.
        timeout: Seconds to wait for the image(s) to render.
        verbose: Enable PlaywrightAuthor debug logging.

    Returns:
        List of saved file paths.
    """
    out_dir = Path(out)
    saved: list[str] = []

    with Browser(verbose=verbose) as browser:
        # Fresh tab in the authenticated context (avoids reusing a stale tab).
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()

        logger.info(f"Opening {project_url}")
        page.goto(project_url, wait_until="domcontentloaded")

        prompt_box = page.locator('div[role="textbox"][contenteditable="true"]')
        try:
            prompt_box.wait_for(state="visible", timeout=30_000)
        except Exception:
            logger.error("Prompt box not found — are you logged into Google?")
            return saved

        # 1) Drive the in-box parameters before typing.
        _apply_parameters(page, model, aspect, count)

        # 2) Type the prompt into the Slate contenteditable.
        logger.info(f"Typing prompt: {prompt!r}")
        prompt_box.click()
        prompt_box.press("Control+a")
        prompt_box.press("Delete")
        prompt_box.type(prompt, delay=10)

        # 3) Snapshot existing results, then submit.
        results = page.locator('img[src*="media.getMediaUrlRedirect"]')
        before = {results.nth(i).get_attribute("src") for i in range(results.count())}

        submit = page.locator('button:has(i.google-symbols:text("arrow_forward"))').last
        submit.wait_for(state="visible", timeout=10_000)
        page.wait_for_function(
            "el => el && el.getAttribute('aria-disabled') !== 'true'",
            arg=submit.element_handle(),
            timeout=10_000,
        )
        logger.info("Submitting generation request")
        submit.click()

        # 4) Poll for genuinely new images.
        logger.info("Waiting for image(s) to render...")
        new_srcs: list[str] = []
        for _ in range(timeout):
            current = [
                results.nth(i).get_attribute("src") for i in range(results.count())
            ]
            new_srcs = [s for s in current if s and s not in before]
            if new_srcs:
                page.wait_for_timeout(2000)  # let the full batch settle
                current = [
                    results.nth(i).get_attribute("src") for i in range(results.count())
                ]
                new_srcs = [s for s in current if s and s not in before]
                break
            page.wait_for_timeout(1000)

        if not new_srcs:
            logger.error("Timed out waiting for the image; it may still be processing.")
            return saved

        logger.info(f"{len(new_srcs)} image(s) generated")

        # 5) Download each new image via the browser's request context.
        out_dir.mkdir(parents=True, exist_ok=True)
        for n, src in enumerate(new_srcs, start=1):
            resp = page.context.request.get(urljoin(page.url, src))
            if not resp.ok:
                logger.warning(f"Failed to fetch image {n}: HTTP {resp.status}")
                continue
            path = out_dir / f"flow_{n}.jpeg"
            path.write_bytes(resp.body())
            logger.info(f"Saved {path} ({len(resp.body())} bytes)")
            saved.append(str(path))

    return saved


if __name__ == "__main__":
    fire.Fire(generate)
