import pytest
from hypothesis import given, strategies as st

from parking_fee import minutes_parked, hourly_rate, format_plate

# Inputs of every flavour: arbitrary text, None, numbers, lists, bytes ...
anything = st.text() | st.none() | st.integers() | st.floats() | st.binary() | st.lists(st.integers())


# ---------------------------------------------------------------------------
# 1. "No crash" fuzz tests: bad input may be rejected, but only with ValueError.
# ---------------------------------------------------------------------------
@given(anything)
def test_minutes_parked_no_crash(s):
    try:
        minutes_parked(s)
    except ValueError:
        pass
    except Exception as e:
        assert False, f"minutes_parked crashed with: {type(e).__name__}: {e}"


@given(anything)
def test_hourly_rate_no_crash(s):
    try:
        hourly_rate(s)
    except ValueError:
        pass
    except Exception as e:
        assert False, f"hourly_rate crashed with: {type(e).__name__}: {e}"


@given(anything)
def test_format_plate_no_crash(s):
    try:
        format_plate(s)
    except ValueError:
        pass
    except Exception as e:
        assert False, f"format_plate crashed with: {type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# 2. Property tests on valid input.
# ---------------------------------------------------------------------------
@given(st.integers(0, 23), st.integers(0, 59), st.integers(0, 23), st.integers(0, 59))
def test_minutes_parked_properties(h1, m1, h2, m2):
    entry, exit_time = h1 * 60 + m1, h2 * 60 + m2
    text = f"{h1:02d}:{m1:02d}-{h2:02d}:{m2:02d}"
    if exit_time >= entry:
        result = minutes_parked(text)
        assert result == exit_time - entry and 0 <= result < 24 * 60
    else:
        with pytest.raises(ValueError):
            minutes_parked(text)


@given(st.sampled_from(["bike", "car", "truck"]), st.text(alphabet=" \t"), st.booleans())
def test_hourly_rate_valid(vehicle, pad, upper):
    v = vehicle.upper() if upper else vehicle
    assert hourly_rate(pad + v + pad) in (10, 30, 60)


@given(st.from_regex(r"[A-Za-z]{2}[0-9]{2}[A-Za-z]{1,2}[0-9]{4}", fullmatch=True))
def test_format_plate_valid(plate):
    out = format_plate(plate)
    assert out == out.upper() and out.replace(" ", "") == plate.upper()
    assert len(out.split(" ")) == 4


# ---------------------------------------------------------------------------
# 3. Explicit regression cases for edge cases found by the fuzzer.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("bad", [None, "", "09:30", "09:30-", "-11:45", "9-11", "ab:cd-ef:gh",
                                 "09:30-11:45-12:00", "25:00-26:00", "09:60-10:00", "10:00-09:00",
                                 "-1:00-2:00", "٠٩:٣٠-١١:٤٥", "09:30 - 11:4 5", 930, ["09:30-10:00"]])
def test_minutes_parked_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        minutes_parked(bad)


@pytest.mark.parametrize("bad", [None, "", "   ", "bus", "cars", "car truck", 5, b"car"])
def test_hourly_rate_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        hourly_rate(bad)


@pytest.mark.parametrize("bad", [None, "", "ka01", "ka01ab123", "ka01ab12345", "1234567890", "ka-1ab1234",
                                 "ßß01ab1234", "ka01ab12٣4", "ka 01 ab 1234", 12345])
def test_format_plate_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        format_plate(bad)


def test_known_good_values():
    assert minutes_parked("09:30-11:45") == 135
    assert minutes_parked("00:00-23:59") == 1439
    assert hourly_rate("  Truck ") == 60
    assert format_plate("ka01ab1234") == "KA 01 AB 1234"
    assert format_plate(" KA01A1234 ") == "KA 01 A 1234"
