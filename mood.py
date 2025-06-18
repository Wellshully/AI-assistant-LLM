import random

MOOD_LIST = ["平靜", "煩躁", "興奮", "無聊"]

class MoodManager:
    def __init__(self):
        self.mood = "平靜"

    def update(self, user_input: str):
        lowered = user_input.lower()
        if any(word in lowered for word in ["謝謝", "幹得好", "很棒"]):
            self.mood = "興奮"
        elif any(word in lowered for word in ["吵", "煩", "閉嘴"]):
            self.mood = "煩躁"
        elif any(word in lowered for word in ["哈囉", "你好", "在嗎"]):
            self.mood = "平靜"
        else:
            self.mood = random.choices(
                [self.mood, "無聊"], weights=[0.7, 0.3]
            )[0]

    def get_prompt_prefix(self):
        return f"請以[{self.mood}]心情回答以下問題："