# Change: Fix specification discrepancies between OpenSpec, memory bank, and implementation

## Why

A compliance audit identified 4 discrepancies between the OpenSpec specifications, memory bank documentation, and actual implementation:

1. **Logging uses wrong env var**: Code uses `LOG_LEVEL` but spec requires `BGU_LOG_LEVEL`
2. **Memory bank references non-existent sandbox module**: Documentation describes feature that doesn't exist
3. **Memory bank references non-existent utils module**: Planned extraction never completed
4. **Test coverage below spec targets**: 56% actual vs 85% target

These discrepancies cause confusion, reduce trust in documentation, and indicate incomplete work.

## What Changes

### 1. Code Fix: Logging Environment Variable
- Update `src/background_utils/logging.py` to use `BGU_LOG_LEVEL` instead of `LOG_LEVEL`
- Maintains consistency with project-wide `BGU_` prefix convention

### 2. Documentation Fix: Memory Bank Cleanup
- Remove references to non-existent `background_utils.sandbox` module
- Clarify `utils/` as planned future work in "What's left to build"
- Update `systemPatterns.md` to reflect actual architecture

### 3. Documentation Fix: Update Progress Tracking
- Update `progress.md` to accurately reflect current state
- Move sandbox/utils to explicit "planned" section
- Update test coverage status

### 4. Test Coverage Improvement
- Add tests to improve coverage toward 85% target
- Focus on highest-value modules: wifi.py, manager.py, gmail_notifier.py

## Impact

- **Affected specs**: logging/spec.md, testing/spec.md
- **Affected code**: `src/background_utils/logging.py`
- **Affected docs**: `memory-bank/systemPatterns.md`, `memory-bank/progress.md`
- **Risk**: Low - primarily documentation alignment with minor code fix
- **Benefit**: Documentation accurately reflects reality; consistent conventions
