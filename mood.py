import random, config, re
from config import GEMINI_API
from google import genai
from google.genai import types
from google.genai.types import HttpOptions
from llm_parse import gen_mood_score
client = genai.Client(
    http_options=HttpOptions(api_version="v1beta"),
    api_key=config.GEMINI_API,
)


class MoodManager:
    def __init__(self):
        self.mood_score = 0
        self.last_change = 0

    def update(self, user_input: str):
        score_delta = self.analyze_input(user_input)
        self.mood_score += score_delta
        self.mood_score = max(-100, min(100, self.mood_score))
        print("mood_score: ", self.mood_score)

    def analyze_input(self, text: str) -> int:
        return gen_mood_score(text)

    def get_mood(self) -> str:
        if self.mood_score >= 40:
            return "開心且非常積極"
        elif self.mood_score >= 15:
            return "開心"
        elif self.mood_score <= -40:
            return "煩躁"
        elif self.mood_score <= -15:
            return "略顯冷淡"
        else:
            return "平常"

    def get_prompt_prefix(self) -> str:
        mood = self.get_mood()
        return f"請以[{mood}]心情回答以下問題："

    def decay(self):
        if self.mood_score > 0:
            self.mood_score -= 1
        elif self.mood_score < 0:
            self.mood_score += 1
