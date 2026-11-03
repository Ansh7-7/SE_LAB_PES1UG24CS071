"""
Lab 6 - Branch Coverage Tests
Application under test: pet_walking_service.py

Goal: make every decision (if / elif / else / for-loop) take BOTH its
True and False outcome at least once, including loop "zero iterations",
"break" exits, and boundary values.

Run:
    coverage run --branch -m pytest BranchCoverageTest_pet_walking_service.py
    coverage report -m
"""
import pytest
from pet_walking_service import process_walking_routes, inspect_gps_collars


def make_route(session_type="standard_30", walks=None, confirmed=True, weekend=False):
    """Helper to build a route dictionary."""
    return {
        "route_confirmed": confirmed,
        "session_type": session_type,
        "is_weekend": weekend,
        "walks": walks if walks is not None else [],
    }


# ===========================================================================
# process_walking_routes - input validation
# ===========================================================================

# Branch: isinstance check TRUE -> raise
def test_routes_not_a_list_raises():
    with pytest.raises(ValueError):
        process_walking_routes({"route": 1}, 5.0)


# Branch: negative fee TRUE -> raise
def test_negative_fee_raises():
    with pytest.raises(ValueError):
        process_walking_routes([], -0.01)


# Branch: fee == 0 is valid (boundary of "< 0")
def test_zero_transport_fee_is_valid():
    routes = [make_route("standard_30", [{"num_pets": 1}], weekend=True)]
    result = process_walking_routes(routes, 0.0)
    assert result == {"total_revenue": 27.0, "status": "COMPLETED"}


# ===========================================================================
# process_walking_routes - outer route loop
# ===========================================================================

# Branch: route loop runs zero times; total == 0 -> ZERO_EARNINGS
def test_empty_route_list():
    result = process_walking_routes([], 5.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_EARNINGS"}


# Branch: route_confirmed False -> continue (explicit False)
def test_unconfirmed_route_skipped():
    routes = [make_route("standard_60", [{"num_pets": 2}], confirmed=False)]
    result = process_walking_routes(routes, 5.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_EARNINGS"}


# Branch: route_confirmed key missing -> defaults to False -> skipped
def test_route_missing_confirmed_key_skipped():
    routes = [{"session_type": "standard_30", "walks": [{"num_pets": 1}]}]
    result = process_walking_routes(routes, 5.0)
    assert result["status"] == "ZERO_EARNINGS"


# Mix of skipped and processed routes: only the confirmed one counts
def test_mixed_confirmed_and_unconfirmed_routes():
    routes = [
        make_route("standard_30", [{"num_pets": 1}], confirmed=False),
        make_route("standard_30", [{"num_pets": 1}], confirmed=True),
    ]
    result = process_walking_routes(routes, 5.0)
    assert result == {"total_revenue": 27.0, "status": "COMPLETED"}


# ===========================================================================
# process_walking_routes - session type if / elif / elif / else
# ===========================================================================

# Branch: session_type == "standard_60" TRUE -> 35 + 1*5 = 40
def test_session_standard_60():
    routes = [make_route("standard_60", [{"num_pets": 1}])]
    assert process_walking_routes(routes, 5.0)["total_revenue"] == 40.0


# Branch: "standard_30" TRUE (original example test) -> 22 + 5 = 27
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


# Branch: "express_15" TRUE -> 14 + 2*5 = 24
def test_session_express_15():
    routes = [make_route("express_15", [{"num_pets": 2}])]
    assert process_walking_routes(routes, 5.0)["total_revenue"] == 24.0


# Branch: else (unknown session type) -> incident, route skipped
def test_unknown_session_type_skipped():
    routes = [make_route("premium_90", [{"num_pets": 2}])]
    result = process_walking_routes(routes, 5.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_EARNINGS"}


# Branch: session_type key missing -> defaults to "standard_30"
# Also: walks entries use all default keys except num_pets
def test_default_session_type_is_standard_30():
    routes = [{"route_confirmed": True, "walks": [{"num_pets": 1}]}]
    assert process_walking_routes(routes, 5.0)["total_revenue"] == 27.0


# ===========================================================================
# process_walking_routes - inner walk loop
# ===========================================================================

# Branch: walk loop runs zero times (empty list) + weekend TRUE
# earnings = 0 walks + 7 transport = 7
def test_confirmed_route_no_walks_on_weekend():
    routes = [make_route("standard_30", [], weekend=True)]
    result = process_walking_routes(routes, 7.0)
    assert result == {"total_revenue": 7.0, "status": "COMPLETED"}


# Branch: "walks" key missing -> default [] ; weekend FALSE -> ZERO_EARNINGS
def test_confirmed_route_missing_walks_key():
    routes = [{"route_confirmed": True, "session_type": "express_15"}]
    result = process_walking_routes(routes, 7.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_EARNINGS"}


# Branch: num_pets <= 0 TRUE (zero and negative), then loop continues
# to a valid walk: 22 + 5 = 27, incidents = 2
def test_invalid_pet_counts_skipped():
    walks = [{"num_pets": 0}, {"num_pets": -3}, {"num_pets": 1}]
    result = process_walking_routes([make_route("standard_30", walks)], 5.0)
    assert result == {"total_revenue": 27.0, "status": "COMPLETED"}


# Branch: num_pets key missing -> default 0 -> incident
def test_walk_missing_num_pets_key():
    result = process_walking_routes([make_route("standard_30", [{}])], 5.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_EARNINGS"}


# Boundary: num_pets == 3 is NOT a large group -> 22 + 3*5 = 37
def test_three_pets_regular_pricing():
    routes = [make_route("standard_30", [{"num_pets": 3}])]
    assert process_walking_routes(routes, 5.0)["total_revenue"] == 37.0


# Boundary: num_pets == 4 IS a large group -> (22 + 4*8) * 0.9 = 48.6
def test_four_pets_large_group_discount():
    routes = [make_route("standard_30", [{"num_pets": 4}])]
    assert process_walking_routes(routes, 5.0)["total_revenue"] == 48.6


# Large group + meds on standard_60: (35 + 5*8) * 0.9 = 67.5, + 6 = 73.5
def test_large_group_with_meds_standard_60():
    routes = [make_route("standard_60", [{"num_pets": 5, "needs_meds": True}])]
    assert process_walking_routes(routes, 5.0)["total_revenue"] == 73.5


# Branch: needs_meds TRUE on regular walk -> 14 + 5 + 6 = 25
def test_meds_surcharge_regular_walk():
    routes = [make_route("express_15", [{"num_pets": 1, "needs_meds": True}])]
    assert process_walking_routes(routes, 5.0)["total_revenue"] == 25.0


# ===========================================================================
# process_walking_routes - aggression alert branches
# ===========================================================================

# Branch: aggression TRUE + session != standard_60 -> earns 0 for that walk
# but meds surcharge is STILL applied: 0 + 6 = 6
def test_aggression_non_60_still_charges_meds():
    walks = [{"num_pets": 2, "aggression_alert": True, "needs_meds": True}]
    result = process_walking_routes([make_route("express_15", walks)], 5.0)
    assert result == {"total_revenue": 6.0, "status": "COMPLETED"}


# Branch: aggression TRUE + session != standard_60, meds FALSE, then a
# normal walk afterwards still counts: 0 + (22 + 10) = 32
def test_aggression_non_60_loop_continues():
    walks = [{"num_pets": 1, "aggression_alert": True}, {"num_pets": 2}]
    result = process_walking_routes([make_route("standard_30", walks)], 5.0)
    assert result["total_revenue"] == 32.0


# Branch: aggression TRUE + standard_60 -> route earnings wiped, BREAK.
# Earlier earnings (40 + 6 meds) are reset; meds on the aggressive walk
# and the walk after the break are never added -> ZERO_EARNINGS
def test_aggression_standard_60_wipes_route_and_breaks():
    walks = [
        {"num_pets": 1, "needs_meds": True},
        {"num_pets": 1, "aggression_alert": True, "needs_meds": True},
        {"num_pets": 3},
    ]
    result = process_walking_routes([make_route("standard_60", walks)], 5.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_EARNINGS"}


# After a standard_60 break, weekend fee is still added and the next
# route is still processed: (0 + 5 weekend) + (22 + 5) = 32
def test_aggression_break_then_weekend_and_next_route():
    routes = [
        make_route("standard_60", [{"num_pets": 1, "aggression_alert": True}], weekend=True),
        make_route("standard_30", [{"num_pets": 1}]),
    ]
    result = process_walking_routes(routes, 5.0)
    assert result == {"total_revenue": 32.0, "status": "COMPLETED"}


# ===========================================================================
# process_walking_routes - final status branches
# ===========================================================================

# Boundary: exactly 4 incidents -> NOT an audit -> COMPLETED
def test_exactly_four_incidents_not_audit():
    walks = [{"num_pets": 0}, {"num_pets": 0}, {"num_pets": 0}, {"num_pets": 0}, {"num_pets": 1}]
    result = process_walking_routes([make_route("standard_30", walks)], 5.0)
    assert result == {"total_revenue": 27.0, "status": "COMPLETED"}


# Branch: incident_count > 4 TRUE -> INCIDENT_AUDIT (with revenue)
# Route A: 0 pets, -1 pets, aggressive (3 incidents), 2 pets (+32)
# Route B (standard_60): 1 pet (+40), aggressive -> reset, break (incident 4)
# Route C: unknown type (incident 5)
def test_more_than_four_incidents_audit():
    routes = [
        make_route("standard_30", [
            {"num_pets": 0},
            {"num_pets": -1},
            {"num_pets": 1, "aggression_alert": True},
            {"num_pets": 2},
        ]),
        make_route("standard_60", [{"num_pets": 1}, {"num_pets": 1, "aggression_alert": True}]),
        make_route("premium_90", [{"num_pets": 1}]),
    ]
    result = process_walking_routes(routes, 5.0)
    assert result == {"total_revenue": 32.0, "status": "INCIDENT_AUDIT"}


# INCIDENT_AUDIT takes priority over ZERO_EARNINGS when revenue is 0
def test_audit_takes_priority_over_zero_earnings():
    walks = [{"num_pets": 0}] * 5
    result = process_walking_routes([make_route("standard_30", walks)], 5.0)
    assert result == {"total_revenue": 0.0, "status": "INCIDENT_AUDIT"}


# Rounding: three large-group express walks -> 3 * (14 + 32) * 0.9 = 124.2
def test_revenue_is_rounded_to_two_decimals():
    walks = [{"num_pets": 4}] * 3
    result = process_walking_routes([make_route("express_15", walks)], 5.0)
    assert result == {"total_revenue": 124.2, "status": "COMPLETED"}


# ===========================================================================
# inspect_gps_collars
# ===========================================================================

# Branch: "not collar_matrix" TRUE for empty list
def test_gps_empty_list_no_data():
    assert inspect_gps_collars([]) == "NO_DATA"


# Branch: "not collar_matrix" TRUE for None
def test_gps_none_no_data():
    assert inspect_gps_collars(None) == "NO_DATA"


# Branch: weak signal, streak reaches 2 -> LOST_SIGNAL_ALERT
def test_gps_two_consecutive_weak_signals():
    assert inspect_gps_collars([[50, 10, 15]]) == "LOST_SIGNAL_ALERT"


# Branch: weak signal but streak < 2, then strong signal resets streak
def test_gps_alternating_signals_online():
    assert inspect_gps_collars([[50, 10, 60, 15, 70]]) == "ONLINE"


# Boundary: signal == 20 is NOT weak
def test_gps_signal_exactly_20_is_ok():
    assert inspect_gps_collars([[20, 20, 20]]) == "ONLINE"


# Boundary: 19 is weak; two 19s in a row -> alert
def test_gps_signal_19_is_weak():
    assert inspect_gps_collars([[19, 19]]) == "LOST_SIGNAL_ALERT"


# Branch: inner loop runs zero times (collar with no logs)
def test_gps_collar_with_empty_logs():
    assert inspect_gps_collars([[]]) == "ONLINE"


# Streak resets per collar: one weak at end of collar 1 and one weak at
# start of collar 2 are NOT consecutive
def test_gps_streak_resets_between_collars():
    assert inspect_gps_collars([[90, 10], [15, 90]]) == "ONLINE"


# Outer loop moves on: first collar healthy, second collar loses signal
def test_gps_second_collar_lost():
    assert inspect_gps_collars([[80, 90], [10, 5]]) == "LOST_SIGNAL_ALERT"


# Single collar ending on a weak signal (streak 1) -> still ONLINE
def test_gps_single_weak_signal_at_end():
    assert inspect_gps_collars([[90, 90, 5]]) == "ONLINE"
