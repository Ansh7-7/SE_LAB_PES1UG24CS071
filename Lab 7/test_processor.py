import math

from hypothesis import given, settings, strategies as st
from processor import parse_walk_schedule, compute_pace_per_pet, lookup_temperament_surcharge


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Completely random / malformed input (the core fuzzing strategy).
any_input = st.text() | st.none()

# "Almost valid" inputs that look like real data, so the fuzzer also reaches
# the logic after the parsing step (zero/negative numbers, bad flags, etc.).
schedule_like = st.builds(
    lambda p, m, w, sep: f"{p}{sep}{m}{sep}{w}",
    st.integers(min_value=-100, max_value=100),
    st.integers(min_value=-100, max_value=500),
    st.sampled_from(["YES", "NO", "yes", " no ", "MAYBE", ""]),
    st.sampled_from(["-", "--", " - "]),
)

pace_like = st.builds(
    lambda m, p: f"{m}/{p}",
    st.floats(allow_nan=True, allow_infinity=True) | st.integers(-100, 100),
    st.floats(allow_nan=True, allow_infinity=True) | st.integers(-100, 100),
)

temperament_like = st.sampled_from(
    ["CALM", "PLAYFUL", "REACTIVE", "AGGRESSIVE", "calm", "  ply ", "", "XYZ", "AG"]
)


# ---------------------------------------------------------------------------
# 1. parse_walk_schedule
# ---------------------------------------------------------------------------

@given(any_input)
def test_parse_walk_schedule_no_crash(s):
    try:
        result = parse_walk_schedule(s)
    except Exception as e:
        assert False, f"parse_walk_schedule crashed on {s!r} with: {type(e).__name__}: {e}"
    assert isinstance(result, str)


@given(schedule_like)
def test_parse_walk_schedule_structured_no_crash(s):
    try:
        result = parse_walk_schedule(s)
    except Exception as e:
        assert False, f"parse_walk_schedule crashed on {s!r} with: {type(e).__name__}: {e}"
    assert isinstance(result, str)
    # A schedule with zero or negative pets/minutes must never be priced.
    if "Total" in result:
        assert "-" not in result.split("Total")[1], f"Negative total for {s!r}: {result}"


@given(st.integers(1, 10), st.integers(1, 240), st.sampled_from(["YES", "NO"]))
def test_parse_walk_schedule_valid_total(pets, mins, weekend):
    result = parse_walk_schedule(f"{pets}-{mins}-{weekend}")
    expected = (20.0 if mins <= 30 else 35.0) + pets * 5.0 + (15.0 if weekend == "YES" else 0.0)
    assert result == f"Walk: {pets} pets, {mins} mins - Total ${expected:.2f}"


# ---------------------------------------------------------------------------
# 2. compute_pace_per_pet
# ---------------------------------------------------------------------------

@given(any_input)
def test_compute_pace_per_pet_safe(s):
    try:
        result = compute_pace_per_pet(s)
    except Exception as e:
        assert False, f"compute_pace_per_pet crashed on {s!r} with: {type(e).__name__}: {e}"
    assert result is None or isinstance(result, float)


@given(pace_like)
def test_compute_pace_per_pet_structured_safe(s):
    try:
        result = compute_pace_per_pet(s)
    except Exception as e:
        assert False, f"compute_pace_per_pet crashed on {s!r} with: {type(e).__name__}: {e}"
    # Pace must be a real, non-negative number (no nan / inf / negative pace).
    if result is not None:
        assert math.isfinite(result) and result >= 0, f"Bad pace {result} for {s!r}"


@given(st.integers(0, 600), st.integers(1, 20))
def test_compute_pace_per_pet_valid(mins, pets):
    assert compute_pace_per_pet(f"{mins}/{pets}") == round(mins / pets, 2)


# ---------------------------------------------------------------------------
# 3. lookup_temperament_surcharge
# ---------------------------------------------------------------------------

@given(any_input)
def test_lookup_temperament_surcharge_safe(s):
    try:
        result = lookup_temperament_surcharge(s)
    except Exception as e:
        assert False, f"lookup_temperament_surcharge crashed on {s!r} with: {type(e).__name__}: {e}"
    assert result is None or result in (0.0, 5.0, 12.0, 20.0)


@given(temperament_like)
def test_lookup_temperament_surcharge_known_codes(s):
    try:
        result = lookup_temperament_surcharge(s)
    except Exception as e:
        assert False, f"lookup_temperament_surcharge crashed on {s!r} with: {type(e).__name__}: {e}"
    expected = {"CAL": 0.0, "PLY": 5.0, "PLA": 5.0, "REA": 12.0, "AGG": 20.0}
    assert result == expected.get(s.strip().upper()[:3])
