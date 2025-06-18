from google.auth import default
from googleapiclient.discovery import build
from datetime import datetime, date, timedelta
import pytz
creds, _ = default(scopes=["https://www.googleapis.com/auth/calendar"])
service = build("calendar", "v3", credentials=creds)

def add_event(summary, start_dt, end_dt, timezone="Asia/Taipei"):
    event = {
        "summary": summary,
        "start": {"dateTime": start_dt, "timeZone": timezone},
        "end": {"dateTime": end_dt, "timeZone": timezone},
    }
    created_event = service.events().insert(calendarId="primary", body=event).execute()
    print(f"新增行程成功，ID: {created_event['id']}")
    return created_event

def list_events_for_day(date, timezone="Asia/Taipei"):
    tz = pytz.timezone(timezone)
    start_of_day = tz.localize(datetime.combine(date, datetime.min.time()))
    end_of_day = start_of_day + timedelta(days=1)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_of_day.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    if not events:
        print(f"{date} 沒有行程")
    else:
        print(f"{date} 的行程:")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"- {start} {event.get('summary', '無標題')}")
    return events
def delete_event_by_keyword(date_obj, keyword, timezone="Asia/Taipei"):
    events = list_events_for_day(date_obj, timezone)
    matched = [e for e in events if keyword in e.get("summary", "")]
    if not matched:
        print(f"沒有包含「{keyword}」的行程。")
        return False
    for event in matched:
        event_id = event['id']
        summary = event.get("summary", "無標題")
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        print(f"已刪除行程：{summary}（ID: {event_id}）")
    return True

if __name__ == "__main__":
    add_event(
        "睡覺",
        "2025-06-18T15:00:00",
        "2025-06-18T16:00:00"
    )
    list_events_for_day(today)
    delete_event_by_keyword(today, "睡覺")
    list_events_for_day(today)
