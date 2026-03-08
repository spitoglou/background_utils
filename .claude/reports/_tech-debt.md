# Tech Debt Registry

Tracked improvements to address later. Created from reviews, postmortems, and deferred findings.

## Critical

- [ ] **TD-006**: `os._exit(0)` bypasses cleanup in TrayController (manager.py:310, 418)
  - **Impact:** Critical
  - **Detail:** Terminates process without running `finally` blocks, flushing file buffers, or `atexit` handlers. Can corrupt log file or Gmail UID cache mid-write. Replace with `sys.exit(0)` or clean flag-based shutdown.
  - **Source:** Code review 2026-03-08
  - **Created:** 2026-03-08

- [ ] **TD-007**: Gmail IMAP `uid("search", None, ...)` passes `None` where `str` expected (gmail_notifier.py:94)
  - **Impact:** Critical
  - **Detail:** Mypy flags `Argument 2 to "uid" has incompatible type "None"; expected "str"`. Works at runtime but is fragile. Pass `"UTF-8"` or correct charset.
  - **Source:** Code review 2026-03-08
  - **Created:** 2026-03-08

## High

- [ ] **TD-001**: Test coverage at ~56%, target is 85%
  - **Impact:** High
  - **Source:** openspec/specs/testing/spec.md
  - **Created:** 2026-03-08

- [ ] **TD-002**: CI workflow not yet implemented (GitHub Actions)
  - **Impact:** High
  - **Source:** openspec/specs/testing/spec.md
  - **Created:** 2026-03-08

- [ ] **TD-009**: Unreachable code in manager.py:306, 379 and gmail_notifier.py:206
  - **Impact:** High
  - **Detail:** Dead code after `os._exit(0)`, unreachable returns, and unreachable branches flagged by mypy `[unreachable]`. Indicates logic errors or leftover code.
  - **Source:** Code review 2026-03-08
  - **Created:** 2026-03-08

- [ ] **TD-010**: Shell injection risk in `_get_profile_key` (wifi.py:93)
  - **Impact:** High
  - **Detail:** Profile name interpolated with embedded quotes into netsh command: `f'name="{name}"'`. While `shell=False` mitigates full injection, unusual SSIDs could cause parsing issues. Sanitize input.
  - **Source:** Code review 2026-03-08
  - **Created:** 2026-03-08

## Medium

- [ ] **TD-003**: Wi-Fi logic not extracted to utils module
  - **Impact:** Medium
  - **Source:** openspec/specs/wifi/spec.md
  - **Created:** 2026-03-08

- [ ] **TD-004**: No security scanning for credential handling (Gmail passwords, .env files)
  - **Impact:** Medium
  - **Source:** Initial infrastructure audit
  - **Created:** 2026-03-08

- [ ] **TD-011**: `_lazy_import` is not actually lazy (app.py:31-34)
  - **Impact:** Medium
  - **Detail:** Called at module level, so imports happen eagerly during `import background_utils.cli.app`. Misleading name. Either genuinely lazy-load or use normal imports.
  - **Source:** Code review 2026-03-08
  - **Created:** 2026-03-08

- [ ] **TD-012**: `_collect_default_services` swallows import errors silently (manager.py:432-438)
  - **Impact:** Medium
  - **Detail:** Catches bare `Exception` on `my_service` import, downgrading real bugs (syntax errors, missing deps) to warnings. Other services imported without try/except -- inconsistent. Also causes mypy error from `my_run = None` vs `ServiceFunc`.
  - **Source:** Code review 2026-03-08
  - **Created:** 2026-03-08

- [ ] **TD-015**: `logging.py` silently swallows file sink setup errors (logging.py:72-74)
  - **Impact:** Medium
  - **Detail:** Bare `except Exception: pass` means broken file logging is invisible. At minimum log the error to the console sink.
  - **Source:** Code review 2026-03-08
  - **Created:** 2026-03-08

- [ ] **TD-016**: `_create_tray_image` returns `object` not `Image` (manager.py:160)
  - **Impact:** Medium
  - **Detail:** Loses all type information. Use `TYPE_CHECKING` import for PIL.Image to provide correct type hint.
  - **Source:** Code review 2026-03-08
  - **Created:** 2026-03-08

- [ ] **TD-018**: Excessive info-level logging in TrayController menu actions (manager.py:198-313)
  - **Impact:** Medium
  - **Detail:** ~30+ `logger.info()` calls for step-by-step execution tracing ("THREAD: Lock acquired", "THREAD: _do_stop thread started"). Should be `logger.debug()`.
  - **Source:** Code review 2026-03-08
  - **Created:** 2026-03-08

- [ ] **TD-019**: Duplicated chunked-sleep pattern across services
  - **Impact:** Medium
  - **Detail:** `while time.time() < end_time and not stop_event.is_set(): time.sleep(0.5)` duplicated in battery_monitor.py and gmail_notifier.py. Extract to shared utility.
  - **Source:** Code review 2026-03-08
  - **Created:** 2026-03-08

## Low

- [ ] **TD-005**: README lacks detailed usage, troubleshooting, and contribution guide
  - **Impact:** Low
  - **Source:** memory-bank migration
  - **Created:** 2026-03-08

- [ ] **TD-024**: Multiple `Console()` instances with different configs (app.py:11, example.py:11, wifi.py:19)
  - **Impact:** Low
  - **Detail:** Each module creates its own `Console()` with different options. Standardize or share a single instance.
  - **Source:** Code review 2026-03-08
  - **Created:** 2026-03-08

- [ ] **TD-025**: Empty test stubs and duplicate test files
  - **Impact:** Low
  - **Detail:** Several tests are no-ops (`test_email_parsing_error`, `test_service_cleanup`, `test_service_isolation` are `pass`). `test_tray.py` and `test_tray_simple.py` overlap significantly. Consolidate or implement.
  - **Source:** Code review 2026-03-08
  - **Created:** 2026-03-08

## Resolved

- [x] **TD-008**: `example_service.run` missing `stop_event` type annotation (example_service.py:11)
  - **Resolved:** 2026-03-08 — Added `stop_event: threading.Event` annotation

- [x] **TD-013**: Duplicate test definitions in test_example.py and test_suite.py
  - **Resolved:** 2026-03-08 — Deleted `tests/test_example.py`

- [x] **TD-014**: `getattr` used for known Settings fields (gmail_notifier.py:226-227)
  - **Resolved:** 2026-03-08 — Replaced with direct attribute access

- [x] **TD-017**: Redundant `setup_logging()` calls in CLI commands
  - **Resolved:** 2026-03-08 — Removed calls + unused imports from example.py and wifi.py

- [x] **TD-020**: 14 ruff lint violations
  - **Resolved:** 2026-03-08 — Auto-fixed + manual line wraps

- [x] **TD-021**: 200+ mypy errors in test files due to strict mode
  - **Resolved:** 2026-03-08 — Added mypy overrides for `tests.*` and third-party stubs; also created `tests/__init__.py`. Reduced from 219 to 25 errors (remaining are production code).

- [x] **TD-022**: `test.py` debugging script in project root
  - **Resolved:** 2026-03-08 — Moved to `scripts/test.py`

- [x] **TD-023**: Missing `__init__.py` in `tests/services/`
  - **Resolved:** 2026-03-08 — Created empty `tests/services/__init__.py`
