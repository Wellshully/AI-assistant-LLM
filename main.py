import os, json, time
from google import genai
from google.genai import types
from google.genai.types import HttpOptions
from tts import speak
from listen import hotword_listener, record_speech
import asyncio
import weather
from mood import MoodManager
import config
from llm_parse import safe_reply, generate_weather_advice, strip_parentheses

mood_mgr = MoodManager()
MAX_WORDS = config.MAX_WORDS
MEMORY_PATH = config.MEMORY_PATH
MAX_SIZE = config.MAX_SIZE


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
    print("🎤 語音模式已啟動：.............")

    while True:
        w = hotword_listener()
        if w:
            data = weather.fetch_weather()
            result = weather.parse_today_weather(data)
            reply = generate_weather_advice(
                mem,
                mem["conversations"],
                json.dumps(result, ensure_ascii=False),
                MAX_WORDS,
            )
            print("機器人：", reply)
            speak(strip_parentheses(reply))
            time.sleep(0.2)
        else:
            u = record_speech(6)
            while True:
                remember = "請你記住" in u
                mood_mgr.update(u)
                add_conv("user", u, remember)
                prompt = mood_mgr.get_prompt_prefix() + u
                print("你: ", prompt)
                reply = safe_reply(mem, mem["conversations"], prompt, MAX_WORDS)
                print("機器人：", reply)
                speak(strip_parentheses(reply))
                add_conv("assistant", reply, False)
                time.sleep(0.2)
                u = record_speech(6)
