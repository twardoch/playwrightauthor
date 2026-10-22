# this_file: src/playwrightauthor/camoufox_session.py
"""Optional pinned Camoufox launch options with a stable profile-local device."""

import json
import os
import platform
import tempfile
from functools import partial
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .session_errors import EngineUnavailable

PACKAGE_VERSION = "0.5.8"


def _sdk() -> Any:
    """Discover an explicitly installed browser; never fetch its binary here."""
    try:
        if version("camoufox") != PACKAGE_VERSION:
            raise EngineUnavailable(
                "Install playwrightauthor[camoufox] for the tested Camoufox version."
            )
        from camoufox import DefaultAddons
        from camoufox.pkgman import camoufox_path, launch_path
        from camoufox.utils import launch_options

        binary = launch_path(camoufox_path(download_if_missing=False))
    except (ImportError, PackageNotFoundError) as error:
        raise EngineUnavailable(
            "Install playwrightauthor[camoufox], then run python -m camoufox fetch."
        ) from error
    except EngineUnavailable:
        raise
    except Exception as error:
        raise EngineUnavailable(
            "Camoufox is unavailable; run python -m camoufox fetch explicitly."
        ) from error
    host = {"Darwin": "macos", "Linux": "linux", "Windows": "windows"}[
        platform.system()
    ]
    return partial(
        launch_options,
        executable_path=binary,
        os=host,
        exclude_addons=list(DefaultAddons),
    )


def launch_options(directory: Path, options: dict[str, Any]) -> dict[str, Any]:
    """Retain generated device values across interactive/headless profile reuse."""
    generate = _sdk()
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory.chmod(0o700)
    identity = directory / "device.json"
    config: dict[str, Any] = {}
    if identity.exists():
        saved = json.loads(identity.read_text())
        if saved.get("version") != PACKAGE_VERSION or not isinstance(
            saved.get("config"), dict
        ):
            raise ValueError(
                "Camoufox device file is incompatible; choose a new profile."
            )
        config = saved["config"]
    forwarded = dict(options)
    forwarded.pop("viewport", None)
    generated = generate(config=config, no_viewport=True, **forwarded)
    if not identity.exists():
        descriptor, temporary = tempfile.mkstemp(prefix=".device-", dir=directory)
        try:
            with os.fdopen(descriptor, "w") as stream:
                json.dump({"version": PACKAGE_VERSION, "config": config}, stream)
            os.replace(temporary, identity)
        finally:
            Path(temporary).unlink(missing_ok=True)
    return dict(generated)
