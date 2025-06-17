from flask import Flask, request, jsonify
import requests, os
from play import play_mp3

app = Flask(__name__)
os.makedirs("generated", exist_ok=True)

@app.route("/suno_callback", methods=["POST"])
def suno_callback():
    data = request.json
     print("🎵 收到 callback")

    try:
        audio_url = data["data"]["data"][0]["audio_url"]
        title = data["data"]["data"][0]["title"]
        filename = f"generated/{title}.mp3"

        print(f"🎵 下載音樂: {title}")
        r = requests.get(audio_url)
        with open(filename, "wb") as f:
            f.write(r.content)

        print(f"▶️ 播放音樂: {filename}")
        play_mp3(filename)
        return jsonify({"status": "success"})

    except Exception as e:
        print("❌ Callback 處理錯誤:", e)
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5678)
