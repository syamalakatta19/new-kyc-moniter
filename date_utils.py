from datetime import datetime


def convert_date(date_text):

    if not date_text:
        return None

    date_text = str(date_text).strip()

    formats = [
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d"
    ]

    for date_format in formats:

        try:

            return datetime.strptime(
                date_text,
                date_format
            ).date()

        except ValueError:

            continue

    return None