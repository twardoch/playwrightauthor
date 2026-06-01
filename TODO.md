# TODO

## Selectable Browser Engine Support (Chrome for Testing + Optional CloakBrowser)

- [x] T1: Add engine implementation task breakdown to TODO.md
- [x] T2: Add `engine: str` field to `BrowserConfig` in `config.py` (default `"chrome"`)
- [x] T3: Create `src/playwrightauthor/engine.py` — engine protocols and registry
- [x] T4: Create `src/playwrightauthor/engines/chrome.py` — Chrome for Testing adapter (bugfix & update)
- [x] T5: Refactor `author.py` to use engine adapter instead of direct CDP connect
- [x] T6: Write chrome engine adapter tests (mock CDP connect)
- [x] T7: Run `uv run pytest tests/test_doctests.py` & `uv run pytest tests/test_author.py` — check/verify
- [x] T8: Create `src/playwrightauthor/engines/cloak.py` — CloakBrowser adapter (lazy import)
- [x] T9: Write cloak engine adapter tests (mock cloakbrowser import + launch)
- [x] T10: Update CLI `__main__.py` with `--engine` flag and engine status
- [x] T11: Update docs (README, CHANGELOG, WORK.md)
- [x] T12: Run `./test.sh` full pipeline

## Future Work

- [ ] Persistent context API for CloakBrowser engine (deferred to v1 follow-up)
- [ ] use `uvx gitnextver` to commit+push+tag 
- [ ] Pre-commit hooks with `ruff`, `mypy`, `bandit` security scanning
- [ ] Automated semantic versioning based on git tags (already using hatch-vcs)
