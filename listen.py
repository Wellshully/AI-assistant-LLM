import sounddevice as sd, soundfile as sf, queue, json, sys, tempfile, os, time, numpy as np
from vosk import Model, KaldiRecognizer, SetLogLevel
from rapidfuzz import fuzz
from tts import speak
from google.cloud import speech_v1 as speech
# ---------- 基本常數 ----------
DEVICE_ID     = 45
SAMPLE_RATE   = 44100
MODEL_PATH    = "models/vosk-model-small-en-us-0.15"
CMD_MAP = {
    "hey turn off light":      "off_light",
    "hey turn on light":       "on_light",
    "hey shut down my pc":     "pc_off",
    "hey listen":              "llm",
}
THRESHOLD = 95
LANG        = "zh-TW"
SEC_RECORD = 5
# ---------- 公用動作 ----------
def do_light(on: bool):
    print("[ACTION]", "開燈" if on else "關燈")
    text = "好啦~~~ 燈已經打開了。" if on else "我把燈給關了， 房間這麼小為什麼不自己來？"
    speak(text)

def do_shutdown():
    print("[ACTION] Shutdown PC")
    speak("要關機嘍...... 文件沒存別怪我。")
    # os.system(r'ssh user@192.168.1.50 "shutdown /s /f /t 0"')

# ---------- 熱詞比對 ----------
def fuzzy_route(text: str):
    for canon, tag in CMD_MAP.items():
        if fuzz.ratio(text, canon) >= THRESHOLD:
            return tag
    return None

# ---------- 主函式 ----------
def hotword_listener() -> str:
    # 初始化 Vosk
    SetLogLevel(-1)
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    recognizer.SetPartialWords(True)

    # PortAudio stream
    q = queue.Queue()
    def _cb(indata, frames, t, status):
        if status:
            print(status, file=sys.stderr)
        q.put(bytes(indata))

    sd.default.device = (DEVICE_ID, None)
    with sd.RawInputStream(device=DEVICE_ID, samplerate=SAMPLE_RATE,
                           dtype='int16', channels=1,
                           blocksize=8000, callback=_cb):
        print("🎤 正在監聽指令…")
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                txt = json.loads(recognizer.Result())["text"]
                print("t: ", txt)
            else:
                txt = json.loads(recognizer.PartialResult())["partial"]

            if not txt:
                continue

            tag = fuzzy_route(txt.lower())
            if tag == "off_light":
                do_light(False)
            elif tag == "on_light":
                do_light(True)
            elif tag == "pc_off":
                do_shutdown()
            elif tag == "llm":
                speak("幹嘛阿, 有啥事阿~~沒事別叫我")
                return

client = speech.SpeechClient()
def record_speech(sec: int = SEC_RECORD) -> str:
    print(f"🎙️  錄音 {sec} 秒…")
    audio = sd.rec(int(sec * SAMPLE_RATE),
                   samplerate=SAMPLE_RATE,
                   channels=1,
                   dtype='int16',
                   device=DEVICE_ID)
    sd.wait()

    # 轉成 wav bytes
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        sf.write(tmp, audio, SAMPLE_RATE, format="WAV", subtype="PCM_16")
        tmp.seek(0)
        wav_bytes = tmp.read()

    # ---- v1 同步辨識：使用 content=bytes ---------------------
    print("sending to recog....")
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code=LANG,
    )
    audio_obj = speech.RecognitionAudio(content=wav_bytes)
    response = client.recognize(config=config, audio=audio_obj)
    # ----------------------------------------------------------

    if not response.results:
        return ""
    return response.results[0].alternatives[0].transcript.strip()
if __name__ == "__main__":
    hotword_listener()
