import requests
from tts import speak
def send_music_request():
    url = "https://apibox.erweima.ai/api/v1/generate"
    payload = {
        "prompt": "generate 10s guitar riff, please short, metal rock style",
        "style": "Rock",
        "title": "New Song",
        "customMode": True,
        "instrumental": True,
        "model": "V3_5",
        "negativeTags": "Heavy Metal",
        "callBackUrl": "https://4dff-219-91-108-136.ngrok-free.app/suno_callback"
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer 50abadaf1f698522b9830a7e5062fa1d"
    }

    print("🎶 發送創作請求中...")
    res = requests.post(url, json=payload, headers=headers)
    print("✅ 回應: ", res.text)
    speak("要我想一段riff嗎... 可以啊~ 但是可能要幾分鐘...畢竟創作是很花費時間的...")

if __name__ == "__main__":
    input("👉 按 Enter 開始生成音樂...")
    send_music_request()
