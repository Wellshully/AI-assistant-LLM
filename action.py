from tts import speak
import threading
import asyncio
from bleak import BleakClient
import subprocess
import time, os
import weather
import config
REMOTE_USER = config.REMOTE_USER
REMOTE_HOST = config.REMOTE_HOST
BOT_MAC = config.BOT_MAC
WRITE_CHAR_UUID = config.WRITE_CHAR_UUID
PASS = config.PASS

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
def chat_mode():
    speak("幹嘛阿, 有啥事阿~~", local=True)

def do_shutdown():
    print("[ACTION] Shutdown PC")
    speak("我設定8秒後關機...... 你是不會自己關嗎...", local=True)
    time.sleep(8)
    os.system('ssh welly@192.168.66.14 "shutdown /s /t 10"')
