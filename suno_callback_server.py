from flask import Flask, request, jsonify
import os, requests, time
from tts import speak
app = Flask(__name__)
AUDIO_DIR = "./downloads"
os.makedirs(AUDIO_DIR, exist_ok=True)

@app.route("/suno_callback", methods=["POST"])
def suno_callback():
    data = request.json
    print("🎵 收到 callback")
    tracks = data.get("data", {}).get("data", [])
    track = tracks[0] if tracks else None
    if track:
        url = track.get("audio_url")
        print(f"▶️ 下載: {url}")
        r = requests.get(url)
        filename = "downloads\\suno_latest.mp3"
        with open(filename, "wb") as f:
            f.write(r.content)
    
        speak("嘿!聽我說, 我有靈感了, 你要給我專心聽喔!")
        time.sleep(2)
        os.system(f'mpg123 "downloads\\suno_latest.mp3" ')

    return jsonify({"msg": "OK"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5678)
