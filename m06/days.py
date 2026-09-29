### m06/days.py

def days_in_month(month, leap_year=False):
    if isinstance(month, bool) or not isinstance(month, int):
        raise TypeError("month must be an integer")
    if not 1 <= month <= 12:
        raise ValueError("month must be between 1 and 12")
    if not isinstance(leap_year, bool):
        raise TypeError("leap_year must be a boolean")

    if month == 2:
        if leap_year:
            return 29
        return 28

    if month in [4, 6, 9, 11]:
        return 30

    return 31

