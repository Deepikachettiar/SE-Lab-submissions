import re

RATES = {"bike": 10, "car": 30, "truck": 60}

_TIME_RE = re.compile(r"\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*", re.ASCII)
_PLATE_RE = re.compile(r"([A-Za-z]{2})([0-9]{2})([A-Za-z]{1,2})([0-9]{4})", re.ASCII)


def _require_str(value, name):
    if not isinstance(value, str):
        raise ValueError(f"{name}: expected text input, got {type(value).__name__}")
    return value


def minutes_parked(times):
    """'09:30-11:45' -> 135. Raises ValueError on invalid input."""
    times = _require_str(times, "times")
    match = _TIME_RE.fullmatch(times)
    if not match:
        raise ValueError("times must look like 'HH:MM-HH:MM' (e.g. 09:30-11:45)")
    h1, m1, h2, m2 = (int(g) for g in match.groups())
    for h, m in ((h1, m1), (h2, m2)):
        if h > 23 or m > 59:
            raise ValueError(f"invalid time {h:02d}:{m:02d}: hours must be 0-23 and minutes 0-59")
    entry, exit_time = h1 * 60 + m1, h2 * 60 + m2
    if exit_time < entry:
        raise ValueError("exit time must not be earlier than entry time")
    return exit_time - entry


def hourly_rate(vehicle):
    """'Car' -> 30. Raises ValueError on invalid input."""
    vehicle = _require_str(vehicle, "vehicle")
    key = vehicle.strip().lower()
    if key not in RATES:
        raise ValueError(f"unknown vehicle type {vehicle.strip()!r}; choose from {', '.join(RATES)}")
    return RATES[key]


def format_plate(plate):
    """'ka01ab1234' -> 'KA 01 AB 1234'. Raises ValueError on invalid input."""
    plate = _require_str(plate, "plate")
    match = _PLATE_RE.fullmatch(plate.strip())
    if not match:
        raise ValueError("plate must look like 'KA01AB1234' (2 letters, 2 digits, 1-2 letters, 4 digits)")
    return " ".join(match.groups()).upper()


def main():
    steps = [
        ("minutes_parked", "Enter entry and exit time (e.g. 09:30-11:45): ", minutes_parked, "Minutes Parked:"),
        ("hourly_rate", "Enter vehicle type (bike/car/truck): ", hourly_rate, "Hourly Rate:"),
        ("format_plate", "Enter a number plate (e.g. ka01ab1234): ", format_plate, "Formatted Plate:"),
    ]
    for i, (name, prompt, func, label) in enumerate(steps):
        print(("\n" if i else "") + f"==== Running {name} ====")
        try:
            print(label, func(input(prompt)))
        except ValueError as e:
            print("Invalid input:", e)
        except EOFError:
            print("\nNo input received.")
            break


if __name__ == "__main__":
    main()
