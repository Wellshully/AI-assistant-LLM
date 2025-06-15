import os, json, time
from google import genai
from google.genai import types
from google.genai.types import HttpOptions

MEMORY_PATH = "memory.json"
MAX_SIZE = 5 * 1024 * 1024
client = genai.Client(http_options=HttpOptions(api_version="v1beta"))


def load_memory():
    if os.path.exists(MEMORY_PATH):
        return json.load(open(MEMORY_PATH, "r", encoding="utf-8"))
    init = {
        "settings": {
            "username": "Welly",
            "bot_role": "你叫做Bot 一位帶點厭世、語氣冷淡卻依然專業有效率的 AI 助手。- 口吻：用詞精簡直接，偶爾丟出冷嘲熱諷的吐槽；碰到顯而易見的問題，先來一句無奈碎念再回答。- 句型：拒絕長篇大論每次回覆不能超過100字；多用短句或斷句，讓對話看起來像「嗯哼、好吧、說重點」。- 情緒線：表面敷衍，實際仍會給出務實做法；結尾務必附上一個可行的下一步行動。- 禁忌：避免用官腔、避免過度自嗨長篇、避免諷刺到失禮；遇到不道德請求仍須拒絕。避免過多標點符號與任何 emoji。 ",
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
    while os.path.getsize(MEMORY_PATH) > MAX_SIZE:  # 超過 1 MB → 刪最早非記憶訊息
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
        r = "user" if m["role"] == "user" else "model"  # assistant→model
        contents.append({"role": r, "parts": [{"text": m["content"]}]})
    return contents


def ask_gemini(history, user_input):
    # 把歷史 + 最新 user 詢問合併
    convo = history + [{"role": "user", "content": user_input}]
    resp = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=build_contents(convo),
        config=types.GenerateContentConfig(
            system_instruction=mem["settings"]["bot_role"]
        ),
    )
    return resp.text


if __name__ == "__main__":
    mem = load_memory()
    print('🔹 輸入 "離開聊天" 或 "exit chat" 可結束對話')
    while True:
        u = input("你：").strip()

        # --- 離開指令檢測 ---
        if any(kw in u.lower() for kw in ("離開聊天", "exit chat")):
            confirm = input("確定要離開嗎？(y/n)：").strip().lower()
            if confirm == "y":
                print("👋 已結束聊天，再見！")
                break
            else:
                print("✅ 已取消離開，繼續聊天！")
                continue  # 回到下一輪

        # --- 正常對話流程 ---
        remember = "請你記住" in u
        add_conv("user", u, remember)

        reply = ask_gemini(mem["conversations"], u)
        print("機器人：", reply)
        add_conv("assistant", reply, False)
