from backend.calendar.gcal import check_availability as gcal_check, book_slot as gcal_book, suggest_slots as gcal_suggest

def check_availability(date: str) -> str:
    times = gcal_check(date)
    return "\n".join(times)

def suggest_slots(date: str) -> str:
    return gcal_suggest(date)

def book_slot(iso_datetime: str) -> str:
    return gcal_book(iso_datetime)
