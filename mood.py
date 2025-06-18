import random
from config import GEMINI_API
from google import genai
from google.genai import types
from google.genai.types import HttpOptions
client = genai.Client(
    http_options=HttpOptions(api_version="v1beta"),
    api_key=config.GEMINI_API,
)

class MoodManager:
    def __init__(self):
        self.mood_score = 0
        self.last_change = 0
    def gen_mood_score(text: str) -> int:
        if len(text) < 5:
            return 0
        prompt = f"以下是一句使用者說的話。請判斷這句話對 AI 助手的心情會造成多大影響，輸出一個整數，範圍是 -10（非常煩躁）到 +10（非常開心），0 表示中性或無影響。只輸出一個整數：{text}"
        resp = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            config=types.GenerateContentConfig(
                system_instruction="你是一個冷靜理性的分析器，負責從語氣與語意中判斷影響程度。",
                max_output_tokens=20,
            ),
        )
        raw = resp.text.strip()
        try:
            return max(-10, min(10, int(re.search(r"-?\d+", raw).group())))
        except:
            return 0
    def update(self, user_input: str):
        score_delta = self.analyze_input(user_input)
        self.mood_score += score_delta
        self.mood_score = max(-100, min(100, self.mood_score))
        print("mood_score: ", self.mood_score)

    def analyze_input(self, text: str) -> int:
        return gen_mood_score(text)

    def get_mood(self) -> str:
        if self.mood_score >= 40:
            return "興奮"
        elif self.mood_score <= -40:
            return "煩躁"
        elif -15 <= self.mood_score <= 15:
            return "平常"
        else:
            return "無聊"

    def get_prompt_prefix(self) -> str:
        mood = self.get_mood()
        return f"請以[{mood}]心情回答以下問題："

    def decay(self):
        if self.mood_score > 0:
            self.mood_score -= 1
        elif self.mood_score < 0:
            self.mood_score += 1

