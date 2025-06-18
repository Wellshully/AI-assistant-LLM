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

def delete_event_by_keyword(date_obj, keyword, timezone="Asia/Taipei"):
    events = list_events_for_day(date_obj, timezone)
    matched = [e for e in events if keyword in e.get("summary", "")]
    if not matched:
        print(f"沒有包含「{keyword}」的行程。")
        return False
    for event in matched:
        event_id = event["id"]
        summary = event.get("summary", "無標題")
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        print(f"已刪除行程：{summary}（ID: {event_id}）")
    return True
    
def list_events_for_period(start_datetime, end_datetime, timezone="Asia/Taipei"):
    tz = pytz.timezone(timezone)
    if start_datetime.tzinfo is None:
        start_datetime = tz.localize(start_datetime)
    if end_datetime.tzinfo is None:
        end_datetime = tz.localize(end_datetime)

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_datetime.isoformat(),
            timeMax=end_datetime.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = events_result.get("items", [])
    return format_events_output(events, start_datetime, end_datetime)


def format_events_output(events, start_datetime, end_datetime, timezone="Asia/Taipei"):
    tz = pytz.timezone(timezone)
    if start_datetime.tzinfo is None:
        start_datetime = tz.localize(start_datetime)
    if end_datetime.tzinfo is None:
        end_datetime = tz.localize(end_datetime)
        
    if not events:
        return f"{start_datetime.date()} 至 {end_datetime.date()} 沒有行程"
    else:
        lines = [f"{start_datetime.date()} 至 {end_datetime.date()} 的行程:"]
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get('summary', '無標題')
            lines.append(f"- {start} {summary}")
        return "\n".join(lines)

        
def list_events_for_day(date, timezone="Asia/Taipei"):
    tz = pytz.timezone(timezone)
    start_of_day = datetime.combine(date, datetime.min.time())
    end_of_day = start_of_day + timedelta(days=1)
    return list_events_for_period(start_of_day, end_of_day, timezone)


def list_events_for_week(start_date, end_date, timezone="Asia/Taipei"):
    tz = pytz.timezone(timezone)
    start_of_week = datetime.combine(start_date, datetime.min.time())
    end_of_week = datetime.combine(end_date + timedelta(days=1), datetime.min.time())  # 包含最後一天整天
    return list_events_for_period(start_of_week, end_of_week, timezone)


if __name__ == "__main__":
    add_event("睡覺", "2025-06-18T15:00:00", "2025-06-18T16:00:00")
    today = date.today()
    list_events_for_day(today)
    delete_event_by_keyword(today, "睡覺")
    list_events_for_day(today)
