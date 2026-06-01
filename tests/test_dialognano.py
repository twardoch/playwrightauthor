# this_file: tests/test_dialognano.py

from __future__ import annotations

from playwrightauthor import dialognano


def test_notify_interactive_task_includes_profile_service_and_task(monkeypatch) -> None:
    calls: list[tuple[str, str, bool]] = []

    def fake_dialog(
        message: str, title: str = "Message", ok_cancel: bool = False
    ) -> bool:
        calls.append((message, title, ok_cancel))
        return True

    monkeypatch.setattr(dialognano, "dialog", fake_dialog)

    assert dialognano.notify_interactive_task(
        task="Complete sign-in or captcha if prompted.",
        profile="google-primary",
        service="Gemini",
        suppress=False,
    )

    assert len(calls) == 1
    message, title, ok_cancel = calls[0]
    assert title == "PlaywrightAuthor needs your browser"
    assert "Gemini" in message
    assert "google-primary" in message
    assert "Complete sign-in or captcha if prompted." in message
    assert ok_cancel is False


def test_notify_interactive_task_suppression_skips_dialog(monkeypatch) -> None:
    calls = 0

    def fake_dialog(
        message: str, title: str = "Message", ok_cancel: bool = False
    ) -> bool:
        nonlocal calls
        calls += 1
        return True

    monkeypatch.setattr(dialognano, "dialog", fake_dialog)

    assert dialognano.notify_interactive_task(
        task="Complete sign-in.",
        profile="google-primary",
        service="Gemini",
        suppress=True,
    )
    assert calls == 0
