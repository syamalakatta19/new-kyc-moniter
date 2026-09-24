from datetime import date


def calculate_status(expiry_date):

    if expiry_date is None:

        return "Invalid"

    today = date.today()

    days_left = (
        expiry_date - today
    ).days

    if days_left < 0:

        return "Expired"

    elif days_left <= 30:

        return "Expiring Soon"

    else:

        return "Valid"


def get_days_left(expiry_date):

    if expiry_date is None:

        return None

    today = date.today()

    return (
        expiry_date - today
    ).days