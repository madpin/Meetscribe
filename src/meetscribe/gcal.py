import os.path
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_calendar_service():
    """
    Authenticates with Google Calendar API via OAuth 2.0 and returns a service object.
    On first run, this will prompt the user to authorize the application, creating a
    `token.json` file. Subsequent runs will use this token.

    Requires a `credentials.json` file from a Google Cloud project with the
    Calendar API enabled.
    """
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing Google credentials: {e}. Please re-authenticate.")
                os.remove(TOKEN_FILE)
                creds = None # Force re-authentication

        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"\n[Google Calendar] ERROR: Credentials file not found at '{CREDENTIALS_FILE}'.")
                print("Please download your OAuth 2.0 credentials from the Google Cloud Console and place it here.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred building the calendar service: {error}")
        return None

def find_meeting_for_timestamp(service, timestamp: datetime):
    """
    Finds a calendar event that most closely matches the given timestamp.
    It searches within a 4-hour window around the timestamp.
    """
    if not service:
        return None

    time_min_dt = timestamp - timedelta(hours=2)
    time_max_dt = timestamp + timedelta(hours=2)
    time_min = time_min_dt.isoformat() + "Z"
    time_max = time_max_dt.isoformat() + "Z"

    try:
        events_result = service.events().list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        events = events_result.get("items", [])

        if not events:
            return None

        # Find the event start time closest to the audio timestamp
        closest_event = None
        min_diff = float('inf')

        for event in events:
            start_str = event["start"].get("dateTime", event["start"].get("date"))
            event_start_time = datetime.fromisoformat(start_str.replace('Z', '+00:00'))

            # Ensure both datetimes are timezone-aware for correct comparison
            timestamp_aware = timestamp.astimezone(event_start_time.tzinfo)
            diff = abs((event_start_time - timestamp_aware).total_seconds())

            if diff < min_diff:
                min_diff = diff
                closest_event = event

        # Only return a match if it's within a reasonable threshold (e.g., 1 hour)
        if closest_event and min_diff <= 3600:
            return closest_event

    except HttpError as error:
        print(f"An error occurred fetching calendar events: {error}")

    return None
