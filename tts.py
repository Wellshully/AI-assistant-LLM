from elevenlabs.client import ElevenLabs
from elevenlabs import play
_11 = ElevenLabs(api_key="sk_6aea8b24cef93bd18a8c965c8486e39d85076ee9c32661a1")
#female: hkfHEbBvdQFNX4uWHqRF
#male: fQj4gJSexpu8RDE2Ii5m
VOICE_ID  = "hkfHEbBvdQFNX4uWHqRF" 
MODEL_ID  = "eleven_flash_v2_5"
BASE_SETTINGS   = {"stability": 0.95, "similarity_boost": 0.85, "speed": 1.0}
CACHE_DIR = "tts_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
def speak(text: str, mute: bool = False, local: bool = False):
    if local:
        h = hashlib.md5(text.encode("utf-8")).hexdigest()
        filepath = os.path.join(CACHE_DIR, f"{h}.mp3")
        if os.path.exists(filepath):
            if not mute:
                from pydub import AudioSegment
                from pydub.playback import play as pplay
                audio = AudioSegment.from_file(filepath)
                pplay(audio)
            return filepath
        else:
            # 無快取用 ElevenLabs 產生並存檔
            speed = 1.2 if len(text) > 25 else 1.0
            voice_settings = BASE_SETTINGS | {"speed": speed}
            audio_bytes = _11.text_to_speech.convert(
                text=text,
                voice_id=VOICE_ID,
                model_id=MODEL_ID,
                output_format="mp3_44100_128",
                voice_settings=voice_settings,
            )
            with open(filepath, "wb") as f:
                f.write(audio_bytes)
            if not mute:
                from pydub import AudioSegment
                from pydub.playback import play as pplay
                audio = AudioSegment.from_file(filepath)
                pplay(audio)
            return filepath
    else:
        # 直接線上呼叫 ElevenLabs 不快取
        speed = 1.2 if len(text) > 25 else 1.0
        voice_settings = BASE_SETTINGS | {"speed": speed}
        audio_bytes = _11.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ID,
            model_id=MODEL_ID,
            output_format="mp3_44100_128",
            voice_settings=voice_settings,
        )
        if not mute:
            play(audio_bytes)
        return audio_bytes