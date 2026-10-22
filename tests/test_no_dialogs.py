# this_file: tests/test_no_dialogs.py
"""The offline test boundary intercepts the actual native-dialog entry point."""

from unittest.mock import Mock

from playwrightauthor import dialognano


def test_interactive_notice_is_intercepted_by_offline_fixture():
    assert isinstance(dialognano.dialog, Mock), (
        "Unit tests must never call native dialog UI"
    )
    assert (
        dialognano.notify_interactive_task(task="fixture", profile="unit-test") is True
    )
    dialognano.dialog.assert_called_once()
