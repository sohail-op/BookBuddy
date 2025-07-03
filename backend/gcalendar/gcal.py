
import datetime
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = "/etc/secrets/service_account.json"

CALENDAR_ID = os.getenv("CALENDAR_ID")

def format_datetime_range(start_iso, end_iso):
    start = datetime.datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
    end = datetime.datetime.fromisoformat(end_iso.replace("Z", "+00:00"))

    date_str = start.strftime("%B %d, %Y")
    time_range = f"{start.strftime('%I:%M %p')} to {end.strftime('%I:%M %p')}"
    return f"{date_str} — {time_range}"

def get_calendar_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("calendar", "v3", credentials=creds)

def check_availability(date_str: str) -> list:
    service = get_calendar_service()
    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    start = datetime.datetime.combine(date, datetime.time.min).isoformat() + "Z"
    end = datetime.datetime.combine(date, datetime.time.max).isoformat() + "Z"

    events_result = (
        service.events()
        .list(calendarId=CALENDAR_ID, timeMin=start, timeMax=end, singleEvents=True, orderBy="startTime")
        .execute()
    )

    events = events_result.get("items", [])
    
    if not events:
        return ["✅ You're free all day!"]

    readable_events = []
    for event in events:
        start_time = event["start"].get("dateTime", event["start"].get("date"))
        end_time = event["end"].get("dateTime", event["end"].get("date"))
        readable_events.append(f"❌ Busy: {format_datetime_range(start_time, end_time)}")

    return readable_events


from dateutil import parser as date_parser
import datetime

def book_slot(start_time: str, summary: str = "Booked via AI Agent") -> str:
    """
    Books a time slot on the calendar.
    Accepts flexible natural language for start_time.
    """

    try:
        start_dt = date_parser.parse(start_time, fuzzy=True)
        end_dt = start_dt + datetime.timedelta(minutes=30)

        service = get_calendar_service()

        event = {
            "summary": summary,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Kolkata"},
        }

        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return f"Event created: {created_event.get('htmlLink')}"
    
    except (ValueError, TypeError) as e:
        return f"Failed to parse the date/time: {str(e)}"


def suggest_slots(date_str: str) -> str:
    """
    Suggests mock slots for now (you can improve by checking free periods).
    """
    return "Suggested slots: 11:00 AM, 2:00 PM, 4:30 PM"
