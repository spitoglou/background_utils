## 1. Code Fix: Logging Environment Variable

- [x] 1.1 Update `src/background_utils/logging.py` to use `BGU_LOG_LEVEL` instead of `LOG_LEVEL`
- [x] 1.2 Update docstring to reflect correct env var name
- [x] 1.3 Run tests to verify logging still works

## 2. Memory Bank: Remove Non-Existent Module References

- [x] 2.1 Update `memory-bank/systemPatterns.md` - remove sandbox from architecture section
- [x] 2.2 Update `memory-bank/systemPatterns.md` - clarify utils as future work
- [x] 2.3 Update `memory-bank/progress.md` - move sandbox tests to future/planned section
- [x] 2.4 Update `memory-bank/progress.md` - update test coverage status accurately

## 3. Test Coverage Improvement

- [x] 3.1 Add CLI wifi command tests (target: 80%+ coverage for wifi.py) - achieved 96%
- [x] 3.2 Add service manager edge case tests (target: 85%+ coverage) - comprehensive tests exist
- [x] 3.3 Add gmail notifier mock tests (target: 85%+ coverage) - comprehensive tests exist
- [x] 3.4 Run coverage report to verify improvement - 56% -> 65% overall

## 4. Verification

- [x] 4.1 Run full test suite to ensure no regressions - 96 passed, 1 skipped
- [ ] 4.2 Run `openspec validate --specs --strict` to verify specs valid
- [x] 4.3 Verify memory bank files are consistent
- [x] 4.4 Commit changes with descriptive message
