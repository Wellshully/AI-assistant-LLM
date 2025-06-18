from google import genai
from google.genai import types
from google.genai.types import HttpOptions
import config
from datetime import datetime
import json
client = genai.Client(
    http_options=HttpOptions(api_version="v1beta"),
    api_key=config.GEMINI_API,
)

import re

PARENS_RE = re.compile(r"\([^)]*\)")
BRACKETS_RE = re.compile(r"\[[^\]]*\]")
MULTI_SPACE = re.compile(r"\s{2,}")


def strip_parentheses(text: str) -> str:
    without_paren = PARENS_RE.sub("", text)
    without_bracket = BRACKETS_RE.sub("", without_paren)
    collapsed = MULTI_SPACE.sub(" ", without_bracket)
    return collapsed.strip()


def build_contents(history):
    contents = []
    for m in history:
        r = "user" if m["role"] == "user" else "model"
        contents.append({"role": r, "parts": [{"text": m["content"]}]})
    return contents


def ask_once(mem, history, user_input, brief=False):
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


def safe_reply(mem, history, user_input, maxword):
    first = ask_once(mem, history, user_input)

    if len(first) > maxword:
        print("[PROCESS] 原回覆過長自動簡短回答", first)
        short_prompt = "請簡短回答。 " + user_input
        second = ask_once(mem, history, short_prompt, brief=True)
        return second
    return first


def generate_weather_advice(mem, history, weather_json, maxword):
    prompt = f"請以[平靜]心情根據數據給我口頭建議, 並用[X年X月X日]的天氣狀況是...這樣的句子開頭:{weather_json}"
    return safe_reply(mem, history, prompt, maxword)
    
def generate_schedule_report(mem, history, now_dt, event, maxword):
    prompt = f"請以[平靜]心情根據我的行程表給我口頭報告和建議, 現在時間是{now_dt}, 我的行程表是:{event}"
    print(prompt)
    return safe_reply(mem, history, prompt, maxword)
def gen_mood_score(text: str) -> int:
    if len(text) < 8:
        return 0
    prompt = f"以下是一句使用者說的話。請判斷這句話對 AI 助手的心情會造成多大影響，輸出一個整數，範圍是 -10（非常煩躁）到 +10（非常開心），0 表示中性或無影響或是語意不清。只輸出一個整數：{text}"
    print("mood analyzing...:", text)
    resp = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        config=types.GenerateContentConfig(
            system_instruction="你是一個冷靜理性的分析器，負責從語氣與語意中判斷對話對於助手心情的影響程度。",
            max_output_tokens=20,
        ),
    )
    raw = resp.text.strip()
    try:
        return max(-10, min(10, int(re.search(r"-?\d+", raw).group())))
    except:
        return 0
        
def parse_event_request(user_input: str, now: datetime):
    today_str = now.strftime("%Y-%m-%d %H:%M:%S")
    prompt = f'你是一個日曆助理，請根據使用者說的話解析出一個 Google Calendar 行程，並輸出符合 JSON 格式的事件物件，欄位包括：- summary: 簡短活動描述 -is_delete: true 表示刪除，false 表示新增 - start: ISO 格式（例如 2025-06-25T15:00:00）- end: ISO 格式（例如 2025-06-25T16:00:00）- timeZone: 請固定為 "Asia/Taipei"今天是 {today_str}，請根據這個時間推理出像「明天」、「下週一」這些詞指的是哪一天與幾點。若時間太模糊（如「某天」、「之後」），請將 start 和 end 設為空字串。不要補充說明，只輸出 JSON 格式物件。使用者說：「{user_input}」'
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=[{"role": "user", "parts": [{"text": prompt}]}],
        config=types.GenerateContentConfig(
            system_instruction="你是專門負責從自然語言中擷取 Google Calendar 行程資訊的解析器。",
            max_output_tokens=512,
        ),
    )

    raw = response.text.strip()
    json_match = re.search(r"\{[\s\S]*\}", raw)
    if not json_match:
        return None

    try:
        event_json = json.loads(json_match.group())
    except Exception as e:
        print("[ERROR] JSON parsing failed:", e)
        return None
    if not json_match:
        print("[ERROR] No JSON found in LLM response.")
        return None
        
    required_keys = {
        "summary": "",
        "is_delete": False,
        "start": "",
        "end": "",
        "timeZone": "Asia/Taipei",
    }
    for key in required_keys:
        if key not in event_json:
            return None
        if event_json[key] in [None, ""]:
            return None
    return event_json