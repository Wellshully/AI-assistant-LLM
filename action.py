from tts import speak
import subprocess
import time, os

REMOTE_USER = "welly"
REMOTE_HOST = "192.168.66.14"


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
    text = (
        "好啦~~~ 燈已經打開了。" if on else "我把燈給關了， 房間這麼小為什麼不自己來？"
    )
    speak(text)


def chat_mode():
    speak("幹嘛阿, 有啥事阿~~沒事別叫我")


def do_shutdown():
    print("[ACTION] Shutdown PC")
    speak("我設定8秒後關機...... 你是不會自己關嗎...")
    time.sleep(2)
    os.system('ssh welly@192.168.66.14 "shutdown /s /t 6"')
