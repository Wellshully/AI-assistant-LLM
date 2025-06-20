from tts import speak
from ble_worker import BLEWorker
import threading
import asyncio
from bleak import BleakClient
import subprocess
import time, os, json
import weather
import config
import pytz
import calendar_api
import llm_parse
import wol
import pygame
from datetime import datetime, timedelta

REMOTE_USER = config.REMOTE_USER
REMOTE_HOST = config.REMOTE_HOST
BOT_MAC = config.BOT_MAC
WRITE_CHAR_UUID = config.WRITE_CHAR_UUID
PASS = config.PASS
MAX_WORDS = config.MAX_WORDS
_ble = BLEWorker(BOT_MAC, WRITE_CHAR_UUID)
events = []

def add_event(event):
    events.append(event)

def event_checker():
    while True:
        try:
            now = datetime.now()
            to_remove = []
            for e in events:
                if now >= e["time"]:
                    tag = e.get("tag", "")
                    print(e["msg"])
                    msg_alarm="注意注意!!" + e["msg"]
                    speak(msg_alarm)
                    time.sleep(1)
                    if tag == "wake_up":
                        do_light(True)
                        pygame.mixer.init()
                        pygame.mixer.music.load("downloads/morning.mp3")
                        pygame.mixer.music.play()
                    elif tag == "sleep":
                        do_light(False)
                    to_remove.append(e)
            for e in to_remove:
                events.remove(e)
            time.sleep(5)
        except Exception as e:
            print("[ERROR in event_checker]:", e)
def ssh_exec(bat_filename: str):
    cmd = f'ssh {REMOTE_USER}@{REMOTE_HOST} "{bat_filename}"'
    subprocess.run(cmd, shell=True)


def open_yt(url: str):
    ssh_exec(f"open_yt.bat")


def launch_game(game: str):
    ssh_exec("open_cs.bat")


def play_rock():
    ssh_exec("open_song_rock.bat")


def open_mail():
    ssh_exec("open_gmail.bat")


def do_light(on: bool):
    print("[ACTION]", "開燈" if on else "關燈")
    if on:
        _ble.light_on()
    else:
        _ble.light_off()
    time.sleep(1)
    speak("開燈。" if on else "關燈。", local=True)


def type_pass():
    script_path = r"bot_type.sh"
    subprocess.Popen(["bash", script_path, PASS])


import subprocess
import platform


def has_internet(host="google.com") -> bool:
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        out = subprocess.check_output(
            ["ping", param, "1", host],
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def weather_report(mem):
    data = weather.fetch_weather()
    result = weather.parse_today_weather(data)
    reply = llm_parse.generate_weather_advice(
        mem,
        mem["conversations"],
        json.dumps(result, ensure_ascii=False),
        MAX_WORDS,
    )
    print("機器人：", reply)
    speak(llm_parse.strip_parentheses(reply))
    time.sleep(0.2)


def chat_mode():
    if not has_internet():
        print("No internet")
        speak("網路好像有問題喔, 連接不到線上模型", local=True)
        return 0
    else:
        speak("幹嘛阿, 有啥事阿~~", local=True)
        return 1


def schedule_manager(mem):
    if not has_internet():
        print("No internet")
        speak("網路好像有問題喔, 連接不到行程表", local=True)
        return
    today = datetime.now().date()
    weekday = today.weekday()
    monday = today - timedelta(days=weekday)
    sunday = monday + timedelta(days=6)

    tz = pytz.timezone("Asia/Taipei")
    start_datetime = tz.localize(datetime.combine(monday, datetime.min.time()))
    end_datetime = tz.localize(
        datetime.combine(sunday + timedelta(days=1), datetime.min.time())
    )

    events = calendar_api.list_events_for_week(monday, sunday)
    events_clean = calendar_api.format_events_output(
        events, start_datetime, end_datetime
    )
    reply = llm_parse.generate_schedule_report(
        mem,
        mem["conversations"],
        datetime.now(),
        events_clean,
        MAX_WORDS,
    )
    print(reply)
    speak(llm_parse.strip_parentheses(reply))
    speak("你還有需要我安排什麼行程嗎", local=True)
    from listen import record_speech

    u = record_speech(8)
    print("🗣️ 你說了：", u)

    if not u:
        speak("你不說話我就當沒事囉。", local=True)
        return

    now = datetime.now()
    event_data = llm_parse.parse_event_request(u, now=now)
    print(event_data)
    if not event_data:
        speak("我聽不太懂你想安排什麼，再說一次好嗎？", local=True)
        return

    if event_data.get("is_delete", False):
        keyword = event_data.get("summary", "")
        print(keyword)
        if keyword:
            t = datetime.fromisoformat(event_data["start"]).date()
            calendar_api.delete_event_by_keyword(t, keyword)
            speak(f"已刪除 {t.strftime('%m/%d')} 的 {keyword} 行程。")
        else:
            speak("刪除行程失敗，因為你沒有提供活動名稱。", local=True)
    else:
        calendar_api.add_event(
            event_data["summary"],
            event_data["start"],
            event_data["end"],
            event_data.get("timeZone", "Asia/Taipei"),
        )
        speak(f"好，我幫你安排了 {event_data['summary']}。")
def set_alarm():
    if not has_internet():
        print("No internet")
        speak("網路好像有問題喔, 無法使用語音鬧鐘", local=True)
        return
    speak("請說明你想設定什麼鬧鐘", local=True)
    from listen import record_speech
    user_input = record_speech(6)
    if not user_input:
        speak("我聽不太懂你想安排什麼，再說一次好嗎？", local=True)
        return
    alarm = llm_parse.parse_alarm_request(user_input, datetime.now())
    if not alarm:
        speak("這個鬧鐘我不太懂耶，再說一次？", local=True)
        return
    events.append(alarm)
    print(f"[ALARM ADDED] {alarm}")
    msg = f"好的，鬧鐘已設定在 {alarm['time'].strftime('%H:%M')}。"
    if alarm.get("tag") == "wake_up":
        msg += " 到時我會幫你開燈。"
    elif alarm.get("tag") == "sleep":
        msg += " 我會幫你關燈。"
    speak(msg)

def do_power_on():
    print("[ACTION] Wake up PC")
    speak("正在打開你的電腦...", local=True)
    wol.open_pc()


def do_shutdown():
    print("[ACTION] Shutdown PC")
    speak("設定8秒後關機...... ", local=True)
    time.sleep(8)
    os.system('ssh welly@192.168.66.14 "shutdown /s /t 10"')
