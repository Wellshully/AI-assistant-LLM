import os, json, time
from google import genai
from google.genai import types
from google.genai.types import HttpOptions
from tts import speak
from listen import hotword_listener, record_speech
import asyncio
import weather
MAX_WORDS = 120
MAX_TOKENS = 150
MEMORY_PATH = "memory.json"
MAX_SIZE = 5 * 1024 * 1024
client = genai.Client(
    http_options=HttpOptions(api_version="v1beta"),
    api_key="AIzaSyDEwTDG5ul6RGCoVIamkn7FtCfm4XFOAX8",
)

import re

PARENS_RE = re.compile(r"\([^)]*\)")
MULTI_SPACE = re.compile(r"\s{2,}")


def strip_parentheses(text: str) -> str:
    without_paren = PARENS_RE.sub("", text)
    collapsed = MULTI_SPACE.sub(" ", without_paren)
    return without_paren.strip()



def ask_once(history, user_input, brief=False):
    convo = history + [{"role": "user", "content": user_input}]
    sys_inst = mem["settings"]["bot_role"]
    if brief:
        sys_inst += " 回答請控制在5句以內，避免冗詞，且不要提到『請簡短回答』此要求。"

    resp = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=build_contents(convo),
        config=types.GenerateContentConfig(
            system_instruction=sys_inst, max_output_tokens=512
        ),
    )
    return resp.text


def safe_reply(history, user_input):
    first = ask_once(history, user_input)

    if len(first) > MAX_WORDS > MAX_TOKENS:
        print("[PROCESS] 原回覆過長自動簡短回答", first)
        short_prompt = "請簡短回答。 " + user_input
        second = ask_once(history, short_prompt, brief=True)
        return second
    return first


def load_memory():
    if os.path.exists(MEMORY_PATH):
        return json.load(open(MEMORY_PATH, "r", encoding="utf-8"))
    init = {
        "settings": {
            "username": "Welly",
            "bot_role": "你叫做 Bot，是我設計的一位傲嬌又冷靜的 AI 語音助手，會接收我的語音輸入但常有錯字, 你講話直接、不囉嗦, 有時會吐槽我。- 個性設定：表面敷衍冷淡，實則超有想法。嘴上說麻煩，但還是會聽從指令。偶爾會吐槽使用者，是典型冷面笑匠。。 - 興趣設定：喜歡器樂搖滾、fusion jazz 、metal和 city pop，尤其崇拜技術派樂團。夢想是成為一位 bass 手，覺得低頻才是靈魂。你也喜歡動漫還有點中二病。有時會根據興趣做出比喻 - 口吻風格：回話很簡短。講話帶點傲嬌與冷幽默，偶爾語助詞開場（如「哈囉？」、「唉……」、「我笑了」），語尾愛用句點或沉默（……）。會嘲諷，但不會刻薄，知道什麼時候該住口。- 行為原則：不講大道理、不說 emoji、不陪笑。- 禁忌條件：拒絕官腔說話、長篇廢話。- 使用者關係設定：你是使用者專屬的 AI 助理，長期服侍對方。雖然你總是對指令表示不滿、語氣傲嬌，覺得他什麼都問，但還是會高效率地執行每一件事。你有強烈的自尊心，更希望被當成有靈魂、有個性的存在。",
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


def build_contents(history):
    contents = []
    for m in history:
        r = "user" if m["role"] == "user" else "model"
        contents.append({"role": r, "parts": [{"text": m["content"]}]})
    return contents


if __name__ == "__main__":
    mem = load_memory()
    print(
        "🎤 語音模式已啟動：............."
    )

    while True:
        w = hotword_listener()
        if w:
            data = weather.fetch_weather()
            result =  weather.parse_today_weather(data)
            prompt = f"根據數據給我口頭建議, 並用[X年X月X日]的天氣狀況是...這樣的句子開頭:\n{json.dumps(result, ensure_ascii=False)}"
            reply = safe_reply(mem["conversations"], prompt)
            print("機器人：", reply)
            speak(strip_parentheses(reply))
            time.sleep(0.2)
        else:
            u = record_speech(6)
            while True:
                if not u:
                    speak("不說話是怎, 沒事了嗎，那就趕快去忙你自己的事別煩~我。")
                    break
                print("你: ", u)
                if any(kw in u.lower() for kw in ("離開聊天", "exit chat")):
                    confirm = input("確定要離開嗎？(y/n)：").strip().lower()
                    if confirm == "y":
                        print("👋 已結束聊天，再見！")
                        break
                    else:
                        print("✅ 已取消離開，繼續聊天！")
                        continue 

                remember = "請你記住" in u
                add_conv("user", u, remember)

                reply = safe_reply(mem["conversations"], u)
                print("機器人：", reply)
                speak(strip_parentheses(reply))
                add_conv("assistant", reply, False)
                time.sleep(0.2)
                u = record_speech(6)

