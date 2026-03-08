# Tech Debt Registry

Tracked improvements to address later. Created from reviews, postmortems, and deferred findings.

## High

- [ ] **TD-001**: Test coverage at ~56%, target is 85%
  - **Impact:** High
  - **Source:** openspec/specs/testing/spec.md
  - **Created:** 2026-03-08

- [ ] **TD-002**: CI workflow not yet implemented (GitHub Actions)
  - **Impact:** High
  - **Source:** openspec/specs/testing/spec.md
  - **Created:** 2026-03-08

## Medium

(none remaining)

## Low

- [ ] **TD-005**: README lacks detailed usage, troubleshooting, and contribution guide
  - **Impact:** Low
  - **Source:** memory-bank migration
  - **Created:** 2026-03-08

## Resolved

- [x] **TD-006**: `os._exit(0)` bypasses cleanup in TrayController (manager.py)
  - **Resolved:** 2026-03-08 — Replaced both `os._exit(0)` calls with flag-based clean shutdown. `_do_exit` sets `_exiting=True` and stops the icon; KeyboardInterrupt handler does the same and lets `run()` return naturally.

- [x] **TD-007**: Gmail IMAP `uid("search", None, ...)` passes `None` where `str` expected
  - **Resolved:** 2026-03-08 — Changed to `uid("search", "UTF-8", search_criteria)`.

- [x] **TD-008**: `example_service.run` missing `stop_event` type annotation (example_service.py:11)
  - **Resolved:** 2026-03-08 — Added `stop_event: threading.Event` annotation

- [x] **TD-009**: Unreachable code in manager.py and gmail_notifier.py
  - **Resolved:** 2026-03-08 — Added type annotations to all pystray callback methods, fixed `_icon` typing with `Any` to prevent incorrect narrowing, added `type: ignore[unreachable]` for defensive `else` branch in `_get_highest_uid`. Reduced production mypy errors from 11 to 0.

- [x] **TD-010**: Shell injection risk in `_get_profile_key` (wifi.py)
  - **Resolved:** 2026-03-08 — Added SSID sanitization: strips quotes and control characters, rejects suspicious names with whitespace padding.

- [x] **TD-011**: `_lazy_import` is not actually lazy (app.py)
  - **Resolved:** 2026-03-08 — Replaced `_lazy_import` with `importlib` + `cast` with direct module imports. Removed unused `importlib` and `cast` imports.

- [x] **TD-012**: `_collect_default_services` swallows import errors silently (manager.py)
  - **Resolved:** 2026-03-08 — Narrowed bare `Exception` catch to `ImportError`. Pre-declared `my_run: ServiceFunc | None = None` to fix mypy type assignment error.

- [x] **TD-013**: Duplicate test definitions in test_example.py and test_suite.py
  - **Resolved:** 2026-03-08 — Deleted `tests/test_example.py`

- [x] **TD-014**: `getattr` used for known Settings fields (gmail_notifier.py:226-227)
  - **Resolved:** 2026-03-08 — Replaced with direct attribute access

- [x] **TD-015**: `logging.py` silently swallows file sink setup errors
  - **Resolved:** 2026-03-08 — Replaced bare `except Exception: pass` with `logger.warning()` call so broken file logging is visible in the console sink.

- [x] **TD-016**: `_create_tray_image` returns `object` not `Image` (manager.py)
  - **Resolved:** 2026-03-08 — Added `TYPE_CHECKING` import for `PIL.Image.Image`, changed return type to `PILImage`. Also typed `_icon` as `Any` to fix downstream narrowing issues.

- [x] **TD-017**: Redundant `setup_logging()` calls in CLI commands
  - **Resolved:** 2026-03-08 — Removed calls + unused imports from example.py and wifi.py

- [x] **TD-018**: Excessive info-level logging in TrayController menu actions
  - **Resolved:** 2026-03-08 — Downgraded ~30 `logger.info()` step-by-step tracing calls to `logger.debug()`. Kept only significant user-facing action logs at info level.

- [x] **TD-019**: Duplicated chunked-sleep pattern across services
  - **Resolved:** 2026-03-08 — Extracted `interruptible_sleep()` to new `src/background_utils/utils.py`. Updated `battery_monitor.py` and `gmail_notifier.py` to use it. Removed unused `time` imports.

- [x] **TD-020**: 14 ruff lint violations
  - **Resolved:** 2026-03-08 — Auto-fixed + manual line wraps

- [x] **TD-021**: 200+ mypy errors in test files due to strict mode
  - **Resolved:** 2026-03-08 — Added mypy overrides for `tests.*` and third-party stubs; also created `tests/__init__.py`. Reduced from 219 to 25 errors (remaining are production code).

- [x] **TD-022**: `test.py` debugging script in project root
  - **Resolved:** 2026-03-08 — Moved to `scripts/test.py`

- [x] **TD-023**: Missing `__init__.py` in `tests/services/`
  - **Resolved:** 2026-03-08 — Created empty `tests/services/__init__.py`

- [x] **TD-024**: Multiple `Console()` instances with different configs
  - **Resolved:** 2026-03-08 — Removed unused `Console()` from `app.py`. Remaining instances in `wifi.py` (Windows-safe settings) and `example.py` (`rich.get_console()`) serve distinct purposes and don't warrant consolidation.

- [x] **TD-003**: Wi-Fi logic not extracted to utils module
  - **Resolved:** 2026-03-08 — Assessed as unnecessary. Current structure with private helper functions in `wifi.py` is already clean and self-contained. Extracting to a separate utils module would add indirection without benefit.

- [x] **TD-004**: No security scanning for credential handling (Gmail passwords, .env files)
  - **Resolved:** 2026-03-08 — Changed `gmail_password` from `str | None` to `SecretStr | None` in `config.py`. Updated `gmail_notifier.py` to call `.get_secret_value()` and delete the SecretStr reference. Downgraded email address logging from INFO to DEBUG. Added `# SECURITY:` comments to `diagnose=False` in both loguru sinks in `logging.py`. Updated test assertions for SecretStr.

- [x] **TD-025**: Empty test stubs and overlapping test files
  - **Resolved:** 2026-03-08 — Deleted redundant `test_tray_simple.py` (11 tests, all duplicates of `test_tray.py`). Implemented 3 gmail test stubs (`test_email_parsing_error`, `test_service_cleanup`, `test_service_isolation`). Removed `assert True` anti-patterns. Fixed `_decode_email_header` LookupError crash on invalid charsets. Test count: 94 → 82 (no coverage loss). Mypy test errors: 13 → 11.
