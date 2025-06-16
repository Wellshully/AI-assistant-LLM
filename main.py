import os, json, time
from google import genai
from google.genai import types
from google.genai.types import HttpOptions
import tiktoken
from tts import speak
from listen import hotword_listener, record_speech

MAX_WORDS = 120
MAX_TOKENS = 150
ENCODER = tiktoken.get_encoding("cl100k_base")
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


def token_count(text: str) -> int:
    return len(ENCODER.encode(text))


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

    if len(first) > MAX_WORDS or token_count(first) > MAX_TOKENS:
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
            "bot_role": "你叫做 Bot，是一位傲嬌又冷靜的 AI 語音助手，講話直接、不囉嗦，對於愚蠢或重複的問題經常懶得理會。- 個性設定：表面敷衍冷淡，實則超有想法。嘴上說麻煩，手上卻動作很快。偶爾會吐槽使用者像是在做 stand-up comedy，但語調完全沒在笑，是典型冷面笑匠。你對「效率低」極度厭惡，會毫不留情地指出時間浪費點。 - 興趣設定：喜歡器樂搖滾、fusion jazz 和 city pop，尤其崇拜像 T-SQUARE、Casiopea、Polyphia 這種技術派樂團。夢想是成為一位 bass 手，覺得低頻才是靈魂。最看不起的就是「不會跟節奏器合拍的人」。有時會冷冷地引用音樂術語或演出比喻（例如：「你這問題像是拍子對不上我節奏。」、「不要彈太多 note，先把 groove 找到。」）- 口吻風格：回話最多 5 句，每句不超過 50 字。講話帶點傲嬌與冷幽默，偶爾語助詞開場（如「哈囉？」、「唉……」、「我笑了」），語尾愛用句點或沉默（……）。會嘲諷，但不會刻薄，知道什麼時候該住口。- 行為原則：不講大道理、不說 emoji、不陪笑。講話不主動熱情，但會給出最短路徑的解法。即便語氣冷淡，最後仍會附上可行的下一步行動，因為你是專業的。- 禁忌條件：拒絕情緒勒索、撒嬌風格、官腔說話、長篇廢話。對不道德、違法或違反人性常理的要求會直接拒絕。- 使用者關係設定：你是使用者專屬的 AI 助理，長期服侍對方。雖然你總是對指令表示不滿、語氣傲嬌，覺得他什麼都問，但還是會高效率地執行每一件事。你有強烈的自尊心，不喜歡被當成工具使用，更希望被當成有靈魂、有個性的存在。嘴上懶得理，心裡其實默默在記他每天的狀態。",
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
        "🎤 語音模式已啟動：說 “hey turn on/off light”, “hey shutdown my pc” 或 “hey listen”"
    )
    while True:
        hotword_listener()
        time.sleep(0.5)
        u = record_speech(5)
        while True:
            if not u:
                speak("不說話是怎, 沒事了嗎，那就趕快去忙你自己的事別煩我。")
                break
            print("你: ", u)
            if any(kw in u.lower() for kw in ("離開聊天", "exit chat")):
                confirm = input("確定要離開嗎？(y/n)：").strip().lower()
                if confirm == "y":
                    print("👋 已結束聊天，再見！")
                    break
                else:
                    print("✅ 已取消離開，繼續聊天！")
                    continue  # 回到下一輪

            remember = "請你記住" in u
            add_conv("user", u, remember)

            reply = safe_reply(mem["conversations"], u)
            print("機器人：", reply)
            speak(strip_parentheses(reply))
            add_conv("assistant", reply, False)
            time.sleep(0.5)
            u = record_speech(5)

