import os
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_FILE = "token.json"


def get_calendar_service():
    creds = None
    token_json_str = os.getenv("GOOGLE_TOKEN_JSON")

    if token_json_str:
        token_data = json.loads(token_json_str)
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    elif os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    return build("calendar", "v3", credentials=creds)


def create_event(summary: str, start_iso: str, end_iso: str, description: str = "") -> dict:
    service = get_calendar_service()
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")

    event_body = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_iso, "timeZone": "Europe/Moscow"},
        "end": {"dateTime": end_iso, "timeZone": "Europe/Moscow"},
    }

    return service.events().insert(calendarId=calendar_id, body=event_body).execute()
