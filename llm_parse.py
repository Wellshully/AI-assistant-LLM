from google import genai
from google.genai import types
from google.genai.types import HttpOptions
import config
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


def safe_reply(history, user_input, maxword):
    first = ask_once(history, user_input)

    if len(first) > maxword:
        print("[PROCESS] 原回覆過長自動簡短回答", first)
        short_prompt = "請簡短回答。 " + user_input
        second = ask_once(history, short_prompt, brief=True)
        return second
    return first
    
def generate_weather_advice(history, weather_json, maxword):
    prompt = f"根據數據給我口頭建議, 並用[X年X月X日]的天氣狀況是...這樣的句子開頭:\n{weather_json}"
    return safe_reply(history, prompt, maxword)