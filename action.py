from tts import speak
import threading
import asyncio
from bleak import BleakClient
import subprocess
import time, os
import weather
import config
import pytz
import calendar_api
import llm_parse
from datetime import datetime, timedelta
REMOTE_USER = config.REMOTE_USER
REMOTE_HOST = config.REMOTE_HOST
BOT_MAC = config.BOT_MAC
WRITE_CHAR_UUID = config.WRITE_CHAR_UUID
PASS = config.PASS
MAX_WORDS = config.MAX_WORDS

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

    async def ble_send():
        try:
            async with BleakClient(BOT_MAC) as client:
                cmd = bytearray([0x57, 0x01, 0x01 if on else 0x02])
                await client.write_gatt_char(WRITE_CHAR_UUID, cmd)
                print("✅ BLE 指令送出")
        except Exception as e:
            print("❌ BLE 控制失敗:", e)

    threading.Thread(target=lambda: asyncio.run(ble_send()), daemon=True).start()
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
    else:
        today = datetime.now().date()
        weekday = today.weekday() 
        monday = today - timedelta(days=weekday)
        sunday = monday + timedelta(days=6)
        events = calendar_api.list_events_for_week(monday, sunday)
        reply = llm_parse.generate_schedule_report(
                mem,
                mem["conversations"],
                datetime.now(),
                events,
                MAX_WORDS,
            )
        print(reply)
        speak(reply)
def do_shutdown():
    print("[ACTION] Shutdown PC")
    speak("我設定8秒後關機...... 你是不會自己關嗎...", local=True)
    time.sleep(8)
    os.system('ssh welly@192.168.66.14 "shutdown /s /t 10"')
