"""
Lab 6 - Code (Line) Coverage Tests
Application under test: pet_walking_service.py

Goal: execute every line of the application at least once.

Run:
    coverage run -m pytest CodeCoverageTest_pet_walking_service.py
    coverage report -m
"""
import pytest
from pet_walking_service import process_walking_routes, inspect_gps_collars


# ---------------------------------------------------------------------------
# process_walking_routes
# ---------------------------------------------------------------------------

# Original example test: standard_30, 1 pet -> 22 + 1*5 = 27
def test_single_standard_30_walk():
    routes = [
        {
            "route_confirmed": True,
            "session_type": "standard_30",
            "is_weekend": False,
            "walks": [{"num_pets": 1, "aggression_alert": False, "needs_meds": False}]
        }
    ]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 27.0
    assert result["status"] == "COMPLETED"


# Covers the ValueError line: routes is not a list
def test_invalid_routes_type_raises_error():
    with pytest.raises(ValueError):
        process_walking_routes("not a list", 5.0)


# Covers the ValueError line: negative transport fee
def test_negative_transport_fee_raises_error():
    with pytest.raises(ValueError):
        process_walking_routes([], -1.0)


# Covers: standard_60 fee, medication surcharge, weekend transport fee
# 35 + 2*5 = 45, +6 meds = 51, +10 weekend = 61
def test_standard_60_with_meds_on_weekend():
    routes = [
        {
            "route_confirmed": True,
            "session_type": "standard_60",
            "is_weekend": True,
            "walks": [{"num_pets": 2, "aggression_alert": False, "needs_meds": True}]
        }
    ]
    result = process_walking_routes(routes, 10.0)
    assert result["total_revenue"] == 61.0
    assert result["status"] == "COMPLETED"


# Covers: express_15 fee and large-group (>3 pets) discounted pricing
# (14 + 5*8) * 0.90 = 48.6
def test_express_15_large_group_discount():
    routes = [
        {
            "route_confirmed": True,
            "session_type": "express_15",
            "is_weekend": False,
            "walks": [{"num_pets": 5, "aggression_alert": False, "needs_meds": False}]
        }
    ]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 48.6
    assert result["status"] == "COMPLETED"


# Covers: unconfirmed route is skipped ("continue") and ZERO_EARNINGS status
def test_unconfirmed_route_gives_zero_earnings():
    routes = [
        {
            "route_confirmed": False,
            "session_type": "standard_30",
            "walks": [{"num_pets": 2}]
        }
    ]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 0.0
    assert result["status"] == "ZERO_EARNINGS"


# Covers: invalid session type, num_pets <= 0, aggression alert on a
# non-60 session, aggression alert on a standard_60 session (break),
# and the INCIDENT_AUDIT status (more than 4 incidents).
#
# Route A (standard_30): 0 pets (inc 1), -1 pets (inc 2),
#                        aggressive 1 pet (inc 3, +0), 2 pets (+32) -> 32
# Route B (standard_60): 1 pet (+40), aggressive (inc 4) -> reset to 0, break
# Route C (unknown type): inc 5
# Total = 32.0, incidents = 5 -> INCIDENT_AUDIT
def test_multiple_incidents_trigger_audit():
    routes = [
        {
            "route_confirmed": True,
            "session_type": "standard_30",
            "walks": [
                {"num_pets": 0},
                {"num_pets": -1},
                {"num_pets": 1, "aggression_alert": True},
                {"num_pets": 2},
            ],
        },
        {
            "route_confirmed": True,
            "session_type": "standard_60",
            "walks": [
                {"num_pets": 1},
                {"num_pets": 1, "aggression_alert": True},
            ],
        },
        {
            "route_confirmed": True,
            "session_type": "premium_90",
            "walks": [{"num_pets": 1}],
        },
    ]
    result = process_walking_routes(routes, 5.0)
    assert result["total_revenue"] == 32.0
    assert result["status"] == "INCIDENT_AUDIT"


# ---------------------------------------------------------------------------
# inspect_gps_collars
# ---------------------------------------------------------------------------

# Covers: empty input -> NO_DATA
def test_gps_no_data():
    assert inspect_gps_collars([]) == "NO_DATA"


# Covers: two consecutive weak signals (< 20) -> LOST_SIGNAL_ALERT
def test_gps_two_consecutive_weak_signals():
    assert inspect_gps_collars([[50, 10, 15]]) == "LOST_SIGNAL_ALERT"


# Covers: streak reset by a strong signal, and the ONLINE return
def test_gps_weak_signals_not_consecutive_online():
    assert inspect_gps_collars([[50, 10, 60, 15, 70]]) == "ONLINE"
