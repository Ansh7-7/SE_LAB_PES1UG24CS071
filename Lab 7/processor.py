import math

# Business limits used for input validation
MAX_PETS = 10          # max pets in a single walk
MAX_MINS = 240         # max walk length in minutes
MAX_INPUT_LEN = 100    # reject absurdly long inputs (DoS / int-parsing protection)


def _parse_positive_int(text, max_value):
    """Return text as an int in [1, max_value], or None if invalid."""
    text = text.strip()
    # Only plain ASCII digits: rejects '', '+3', '-2', '3.5', '1_000', unicode digits, etc.
    if not text or not text.isascii() or not text.isdigit():
        return None
    value = int(text)
    if value < 1 or value > max_value:
        return None
    return value


def parse_walk_schedule(schedule_spec):
    """Parse 'PETS-MINUTES-YES/NO' and return a price summary, or an error message."""
    if not isinstance(schedule_spec, str):
        return "Invalid schedule: input must be a string"
    if len(schedule_spec) > MAX_INPUT_LEN:
        return "Invalid schedule: input too long"

    parts = schedule_spec.strip().split('-')
    if len(parts) != 3:
        return "Invalid schedule: expected format PETS-MINUTES-YES/NO (e.g. 2-30-YES)"
    pets_str, mins_str, weekend_str = parts

    pets = _parse_positive_int(pets_str, MAX_PETS)
    if pets is None:
        return f"Invalid schedule: pets must be a whole number from 1 to {MAX_PETS}"

    mins = _parse_positive_int(mins_str, MAX_MINS)
    if mins is None:
        return f"Invalid schedule: minutes must be a whole number from 1 to {MAX_MINS}"

    weekend_map = {"YES": 15.0, "NO": 0.0}
    weekend_fee = weekend_map.get(weekend_str.strip().upper())
    if weekend_fee is None:
        return "Invalid schedule: weekend flag must be YES or NO"

    base_fee = 20.0 if mins <= 30 else 35.0
    total = base_fee + (pets * 5.0) + weekend_fee
    return f"Walk: {pets} pets, {mins} mins - Total ${total:.2f}"


def compute_pace_per_pet(walk_metrics_str):
    """Parse 'MINUTES/PETS' and return minutes per pet, or None if invalid."""
    if not isinstance(walk_metrics_str, str) or len(walk_metrics_str) > MAX_INPUT_LEN:
        return None

    parts = walk_metrics_str.split('/')
    if len(parts) != 2:
        return None

    try:
        mins = float(parts[0])
        pets = float(parts[1])
    except ValueError:
        return None

    # Reject nan / inf, negative minutes, and zero or negative pets (division by zero)
    if not (math.isfinite(mins) and math.isfinite(pets)):
        return None
    if mins < 0 or pets <= 0:
        return None

    pace = mins / pets
    if not math.isfinite(pace):   # e.g. huge value divided by a tiny one overflows
        return None
    return round(pace, 2)


def lookup_temperament_surcharge(temperament_code):
    """Return the surcharge for a temperament code, or None if unknown."""
    if not isinstance(temperament_code, str):
        return None

    prefix = temperament_code.strip().upper()[:3]
    surcharges = {
        "CAL": 0.0,   # CALM
        "PLY": 5.0,   # PLY (short code)
        "PLA": 5.0,   # PLAYFUL  (original code crashed: 'PLAYFUL'[:3] == 'PLA')
        "REA": 12.0,  # REACTIVE
        "AGG": 20.0   # AGGRESSIVE
    }
    return surcharges.get(prefix)


def main():
    print("==== Running parse_walk_schedule ====")
    s_input = input("Enter schedule (e.g. 2-30-YES): ")
    print(parse_walk_schedule(s_input))

    print("\n==== Running compute_pace_per_pet ====")
    p_input = input("Enter minutes/pets (e.g. 45/3): ")
    pace = compute_pace_per_pet(p_input)
    if pace is None:
        print("Invalid input: expected MINUTES/PETS with minutes >= 0 and pets > 0 (e.g. 45/3)")
    else:
        print("Pace (min/pet):", pace)

    print("\n==== Running lookup_temperament_surcharge ====")
    t_input = input("Enter temperament code (e.g. CALM, PLAYFUL, AGGRESSIVE): ")
    surcharge = lookup_temperament_surcharge(t_input)
    if surcharge is None:
        print("Invalid input: unknown temperament code (use CALM, PLAYFUL, REACTIVE or AGGRESSIVE)")
    else:
        print("Surcharge: $", surcharge)


if __name__ == "__main__":
    main()
