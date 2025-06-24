# listen.py
import sounddevice as sd, soundfile as sf, queue, json, sys, tempfile, os, time
import numpy as np
from vosk import Model, KaldiRecognizer, SetLogLevel
from rapidfuzz import fuzz
from tts import speak
from google.cloud import speech_v1 as speech
import action, config
import webrtcvad
# ---------------- global ----------------
DEVICE_ID   = config.DEVICE_ID
SAMPLE_RATE = config.SAMPLE_RATE      
MODEL_PATH  = config.MODEL_PATH
CMD_MAP     = config.CMD_MAP
THRESHOLD   = config.THRESHOLD
LANG        = config.LANG
SEC_RECORD  = config.SEC_RECORD
vad = webrtcvad.Vad(2) #voice threshold
FRAME_DURATION_MS = 10
FRAME_LENGTH = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
# ---- ① Vosk Model / Recognizer  ----
SetLogLevel(-1)                          
_VOSK_MODEL = Model(MODEL_PATH)
_RECO = KaldiRecognizer(_VOSK_MODEL, SAMPLE_RATE)
_RECO.SetPartialWords(True)

# ------------------------------------------------
def fuzzy_route(text: str):
    for canon, tag in CMD_MAP.items():
        if fuzz.ratio(text, canon) >= THRESHOLD:
            return tag
    return None

def hotword_listener(mem) -> int:

    q_audio = queue.Queue()

    def _cb(indata, frames, t, status):
        if status:
            print(status, file=sys.stderr)
        if len(indata) >= FRAME_LENGTH:
            try:
                frame = indata[:FRAME_LENGTH]         # 480 samples
                raw_bytes = frame.tobytes()  
                if vad.is_speech(raw_bytes, SAMPLE_RATE):
                    q_audio.put(bytes(indata)) 
            except Exception as e:
                print("[VAD error]", e)

    sd.default.device = (DEVICE_ID, None)
    with sd.RawInputStream(
        device=DEVICE_ID,
        samplerate=SAMPLE_RATE,
        dtype="int16",
        channels=1,
        blocksize=2048,
        callback=_cb,
    )as stream:
        while True:
            try:
                data = q_audio.get(timeout=0.1)  
            except queue.Empty:
                continue

            if _RECO.AcceptWaveform(data):
                txt = json.loads(_RECO.Result())["text"]
                print("🎤 Listening:", txt)
                if not txt:
                    continue

                tag = fuzzy_route(txt.lower())
                if tag == "off_light":
                    action.do_light(False)
                elif tag == "on_light":
                    action.do_light(True)
                elif tag == "pc_off":
                    action.do_shutdown()
                elif tag == "pc_on":
                    action.do_power_on()
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
                elif tag == "set_alarm":
                    stream.close()
                    action.set_alarm()
                    return 0
                elif tag == "schedule":
                    stream.close()
                    action.schedule_manager(mem)
                    return 0
                elif tag == "llm":
                    if action.chat_mode():
                        return 1
                elif tag == "weather":
                    action.weather_report(mem)

    return 0

# ---------------- Google Speech (record) ----------------
_client = speech.SpeechClient()

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

    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        sf.write(tmp, audio, SAMPLE_RATE, format="WAV", subtype="PCM_16")
        tmp.seek(0)
        wav_bytes = tmp.read()

    recog_cfg = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code=LANG,
    )
    audio_obj = speech.RecognitionAudio(content=wav_bytes)
    resp = _client.recognize(config=recog_cfg, audio=audio_obj)

    if not resp.results:
        return ""
    return resp.results[0].alternatives[0].transcript.strip()

if __name__ == "__main__":
    print(sd.query_devices(DEVICE_ID, "input"))
    hotword_listener({})
