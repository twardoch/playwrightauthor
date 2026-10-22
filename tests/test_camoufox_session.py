# this_file: tests/test_camoufox_session.py
"""Optional Camoufox identity stays stable and private across mode changes."""

import json
from unittest.mock import Mock

import pytest

from playwrightauthor.session_options import SessionOptions


def test_camoufox_keeps_generated_identity_and_separates_profile(tmp_path, monkeypatch):
    from playwrightauthor import camoufox_session

    def generate(**kwargs):
        kwargs["config"].setdefault("navigator.hardwareConcurrency", 8)
        return {"headless": kwargs["headless"], "executable_path": "/fixture/camoufox"}

    sdk = Mock(return_value=generate)
    monkeypatch.setattr(camoufox_session, "_sdk", sdk)
    first = SessionOptions(engine="camoufox", profile="primary", profile_root=tmp_path)
    engine, options = first.launch_options()
    assert engine == "firefox" and options["headless"] is True
    identity = first.profile_dir / "device.json"
    assert (
        json.loads(identity.read_text())["config"]["navigator.hardwareConcurrency"] == 8
    )
    assert identity.stat().st_mode & 0o777 == 0o600
    saved_bytes = identity.read_bytes()
    second = SessionOptions(
        engine="camoufox", profile="primary", mode="interactive", profile_root=tmp_path
    )
    assert second.launch_options()[1]["headless"] is False
    assert identity.read_bytes() == saved_bytes
    assert first.profile_dir == tmp_path / "camoufox" / "primary"


def test_camoufox_rejects_wrong_identity_schema(tmp_path, monkeypatch):
    from playwrightauthor import camoufox_session

    monkeypatch.setattr(camoufox_session, "_sdk", lambda: lambda **kwargs: {})
    options = SessionOptions(engine="camoufox", profile_root=tmp_path)
    options.profile_dir.mkdir(parents=True)
    (options.profile_dir / "device.json").write_text(
        '{"version": "other", "config": {}}'
    )
    with pytest.raises(ValueError, match="device"):
        options.launch_options()


def test_camoufox_missing_package_is_actionable(monkeypatch):
    from importlib.metadata import PackageNotFoundError

    from playwrightauthor import camoufox_session
    from playwrightauthor.session_errors import EngineUnavailable

    def missing(name):
        raise PackageNotFoundError(name)

    monkeypatch.setattr(camoufox_session, "version", missing)
    with pytest.raises(EngineUnavailable, match="camoufox fetch"):
        camoufox_session._sdk()


def test_camoufox_untested_package_version_is_rejected(monkeypatch):
    from playwrightauthor import camoufox_session
    from playwrightauthor.session_errors import EngineUnavailable

    monkeypatch.setattr(camoufox_session, "version", lambda name: "0.0.0")
    with pytest.raises(EngineUnavailable, match="tested Camoufox"):
        camoufox_session._sdk()
