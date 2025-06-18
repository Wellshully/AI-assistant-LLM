import random


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
        text = text.lower()

        if any(w in text for w in ["謝謝", "很棒", "太厲害", "我喜歡你", "好可愛"]):
            return random.randint(5, 10)
        elif any(w in text for w in ["閉嘴", "好煩", "爛死了", "你很吵", "討厭"]):
            return random.randint(-10, -5)
        elif any(w in text for w in ["哈囉", "hi", "在嗎", "你還好嗎"]):
            return random.randint(1, 3)
        elif len(text.strip()) < 4:
            return -1
        return 0

    def get_mood(self) -> str:
        if self.mood_score >= 40:
            return "興奮"
        elif self.mood_score <= -40:
            return "煩躁"
        elif -15 <= self.mood_score <= 15:
            return "平靜"
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

