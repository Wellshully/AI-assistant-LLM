from datetime import datetime, timedelta
from llm_parse import parse_event_request
from calendar_api import add_event, delete_event_by_keyword,list_events_for_week, format_events_output
"""
event_data = parse_event_request("安排這禮拜五下午三點剪頭髮", now=datetime.now())

if event_data:
    print("解析成功:", event_data)
    if event_data.get("is_delete", False):
        keyword = event_data.get("summary", "")
        if keyword:
            t=datetime.fromisoformat(event_data["start"]).date()
            delete_event_by_keyword(t, keyword)
        else:
            print("刪除行程缺少關鍵字 summary，無法刪除")
    else:
        add_event(
            event_data["summary"],
            event_data["start"],
            event_data["end"],
            event_data.get("timeZone", "Asia/Taipei")
        )
else:
    print("解析失敗")
event_data = parse_event_request("安排這禮拜四要上吉他課", now=datetime.now())

if event_data:
    print("解析成功:", event_data)
    if event_data.get("is_delete", False):
        keyword = event_data.get("summary", "")
        if keyword:
            t=datetime.fromisoformat(event_data["start"]).date()
            delete_event_by_keyword(t, keyword)
        else:
            print("刪除行程缺少關鍵字 summary，無法刪除")
    else:
        add_event(
            event_data["summary"],
            event_data["start"],
            event_data["end"],
            event_data.get("timeZone", "Asia/Taipei")
        )
else:
    print("解析失敗")
event_data = parse_event_request("安排這禮拜六要面交吉他", now=datetime.now())

if event_data:
    print("解析成功:", event_data)
    if event_data.get("is_delete", False):
        keyword = event_data.get("summary", "")
        if keyword:
            t=datetime.fromisoformat(event_data["start"]).date()
            delete_event_by_keyword(t, keyword)
        else:
            print("刪除行程缺少關鍵字 summary，無法刪除")
    else:
        add_event(
            event_data["summary"],
            event_data["start"],
            event_data["end"],
            event_data.get("timeZone", "Asia/Taipei")
        )
else:
    print("解析失敗")
 """
today = datetime.now().date()
weekday = today.weekday() 
monday = today - timedelta(days=weekday)
sunday = monday + timedelta(days=6)
events = list_events_for_week(monday, sunday)
print(events)
