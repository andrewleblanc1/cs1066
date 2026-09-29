import pytest

from days import days_in_month


@pytest.mark.parametrize(
    ("month", "expected_days"),
    [
        (1, 31),
        (2, 28),
        (3, 31),
        (4, 30),
        (5, 31),
        (6, 30),
        (7, 31),
        (8, 31),
        (9, 30),
        (10, 31),
        (11, 30),
        (12, 31),
    ],
)
def test_days_in_month_common_year(month, expected_days):
    assert days_in_month(month) == expected_days


def test_days_in_month_february_in_leap_year():
    assert days_in_month(2, leap_year=True) == 29


@pytest.mark.parametrize("month", [0, 13, -1])
def test_days_in_month_rejects_out_of_range_month(month):
    with pytest.raises(ValueError, match="month must be between 1 and 12"):
        days_in_month(month)


@pytest.mark.parametrize("month", ["2", 2.0, True, None])
def test_days_in_month_rejects_non_integer_month(month):
    with pytest.raises(TypeError, match="month must be an integer"):
        days_in_month(month)


@pytest.mark.parametrize("leap_year", [1, "no", None])
def test_days_in_month_rejects_non_boolean_leap_year(leap_year):
    with pytest.raises(TypeError, match="leap_year must be a boolean"):
        days_in_month(2, leap_year=leap_year)