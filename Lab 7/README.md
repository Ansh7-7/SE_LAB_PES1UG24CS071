# L6_L7_13 — Pet Walking Service

Lab 7: Fuzz Testing for Input Validation Bugs (Hypothesis)

## About

Property-based fuzz tests (Hypothesis) for pet walk schedule parsing, pace-per-pet calculation and temperament surcharge lookup. The tests uncovered input validation bugs in `processor.py`, which have been fixed.

## Files

| File | Description |
|------|-------------|
| `processor.py` | Fixed application (hardened against invalid input) |
| `test_processor.py` | Hypothesis fuzz tests for all three functions |
| `Lab7_FuzzTesting_Report.pdf` | Report with screenshots and source code |
| `1_original_run_crash.png` | Original app crashing on `45/0` (ZeroDivisionError) |
| `2_original_run_crash_empty_input.png` | Original app crashing on empty input (ValueError) |
| `3_fuzz_tests_failing.png` | Fuzz tests on original code: 6 failed, 2 passed |
| `4_fixed_run.png` | Fixed app handling the same inputs without crashing |
| `5_fuzz_tests_passing.png` | Fuzz tests on fixed code: 8 passed |

## Bugs found and fixed

- `None` input crashed all three functions (`AttributeError`)
- Wrong number of fields (e.g. `''`, `0--0--YES`, `/`) raised `ValueError`
- `45/0` and `0/0` raised `ZeroDivisionError`; negative / `nan` / `inf` pace was returned silently
- Unknown weekend flag or temperament code raised `KeyError`
- `PLAYFUL` (the prompt's own example) raised `KeyError: 'PLA'`; the table only had `PLY`

## How to run

```
pip install hypothesis pytest
python processor.py
python -m pytest test_processor.py
```
