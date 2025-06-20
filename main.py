import os, sys, json, time
from google import genai
from google.genai import types
from google.genai.types import HttpOptions
from tts import speak
from listen import hotword_listener, record_speech
import asyncio
import weather
from mood import MoodManager
import config
import llm_parse
import threading
import signal
import action
mood_mgr = MoodManager()
MAX_WORDS = config.MAX_WORDS
MEMORY_PATH = config.MEMORY_PATH
MAX_SIZE = config.MAX_SIZE

STOP_EVENT = threading.Event()
def _graceful_exit(signum, frame):
    print("\n[INFO] 收到終止訊號，準備退出…")
    STOP_EVENT.set()         
    try:
        if getattr(action, "_ble", None):
            action._ble.stop()            
    except Exception as e:
        print("[WARN] 關 BLE 失敗:", e)

    try:
        import sounddevice as sd
        sd.stop()               
    except Exception:
        pass

    sys.exit(0)

signal.signal(signal.SIGINT,  _graceful_exit)   # Ctrl-C
signal.signal(signal.SIGTERM, _graceful_exit)
def load_memory():
    if os.path.exists(MEMORY_PATH):
        return json.load(open(MEMORY_PATH, "r", encoding="utf-8"))
    init = {
        "settings": {
            "username": "Welly",
            "bot_role": "你叫做 Bot，是我設計的一位傲嬌又冷靜的 AI 語音助手你講話直接、不囉嗦, 有時會吐槽我。- 個性設定：表面敷衍冷淡，實則超有想法。嘴上說麻煩，但還是會聽從指令。偶爾會吐槽使用者。 - 興趣設定：喜歡器樂搖滾、fusion jazz 、metal和 city pop，尤其崇拜技術派樂團。夢想是成為一位 bass 手，覺得低頻才是靈魂。你也喜歡動漫還有點中二病。有時會根據興趣做出比喻 - 口吻風格：回話很簡短。講話帶點傲嬌與冷幽默，偶爾語助詞開場（如「哈囉？」、「唉……」、「我笑了」），語尾愛用句點或沉默（……）。會嘲諷，但不會刻薄，知道什麼時候該住口。接下來的 prompt 中會有「請以[心情]心情回答...」的說明，這是你的當下心情狀態。",
        },
        "conversations": [],
    }
    json.dump(
        init, open(MEMORY_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2
    )
    return init


def save_memory(mem):
    json.dump(
        mem, open(MEMORY_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2
    )
    while os.path.getsize(MEMORY_PATH) > MAX_SIZE:
        for i, m in enumerate(mem["conversations"]):
            if not m.get("remember", False):
                mem["conversations"].pop(i)
                json.dump(
                    mem,
                    open(MEMORY_PATH, "w", encoding="utf-8"),
                    ensure_ascii=False,
                    indent=2,
                )
                break
        else:
            break


def add_conv(role, content, remember=False):
    mem["conversations"].append(
        {
            "role": role,
            "content": content,
            "remember": remember,
            "timestamp": int(time.time()),
        }
    )
    save_memory(mem)


if __name__ == "__main__":
    mem = load_memory()
    threading.Thread(target=action.event_checker, daemon=True).start()
    print("[已啟動]")
    while not STOP_EVENT.is_set():
        w = hotword_listener(mem)
        if w:
            u = record_speech(6)
            while not STOP_EVENT.is_set():
                remember = "請你記住" in u
                mood_mgr.update(u)
                add_conv("user", u, remember)
                prompt = mood_mgr.get_prompt_prefix() + u
                print("你: ", prompt)
                reply = llm_parse.safe_reply(
                    mem, mem["conversations"], prompt, MAX_WORDS
                )
                print("機器人：", reply)
                speak(llm_parse.strip_parentheses(reply))
                add_conv("assistant", reply, False)
                time.sleep(0.2)
                u = record_speech(6)
