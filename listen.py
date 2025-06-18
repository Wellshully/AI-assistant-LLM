import sounddevice as sd, soundfile as sf, queue, json, sys, tempfile, os, time, numpy as np
from vosk import Model, KaldiRecognizer, SetLogLevel
from rapidfuzz import fuzz
from tts import speak
from google.cloud import speech_v1 as speech
import action
import config

DEVICE_ID = config.DEVICE_ID  # 5
SAMPLE_RATE = config.SAMPLE_RATE  # 16000
MODEL_PATH = config.MODEL_PATH
CMD_MAP = config.CMD_MAP
THRESHOLD = config.THRESHOLD
LANG = config.LANG
SEC_RECORD = config.SEC_RECORD


def fuzzy_route(text: str):
    for canon, tag in CMD_MAP.items():
        if fuzz.ratio(text, canon) >= THRESHOLD:
            return tag
    return None


# ---------- 主函式 ----------
def hotword_listener(mem) -> str:
    # Vosk
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
    with sd.RawInputStream(
        device=DEVICE_ID,
        samplerate=SAMPLE_RATE,
        dtype="int16",
        channels=1,
        blocksize=8000,
        callback=_cb,
    ):
        while True:
            data = q.get()
            if recognizer.AcceptWaveform(data):
                txt = json.loads(recognizer.Result())["text"]
                print("🎤 Listening: ", txt)
                if not txt:
                    continue
                tag = fuzzy_route(txt.lower())
                if tag == "off_light":
                    action.do_light(False)
                elif tag == "on_light":
                    action.do_light(True)
                elif tag == "pc_off":
                    action.do_shutdown()
                elif tag == "open_youtube":
                    action.open_yt("https://www.youtube.com")
                elif tag == "open_cs":
                    action.launch_game("csgo")
                elif tag == "open_mail":
                    action.open_mail()
                elif tag == "play_rock":
                    action.play_rock()
                elif tag == "type_pass":
                    action.type_pass()
                elif tag == "schedule":
                    action.schedule_manager(mem)
                elif tag == "llm":
                    internet = action.chat_mode()
                    if internet:
                        return 0
                elif tag == "weather":
                    return 1

    return 0


client = speech.SpeechClient()


def record_speech(sec: int = SEC_RECORD) -> str:
    print(f"🎙️  錄音 {sec} 秒…")
    audio = sd.rec(
        int(sec * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        device=DEVICE_ID,
    )
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
    info = sd.query_devices(DEVICE_ID, "input")
    print(info)

    hotword_listener()
