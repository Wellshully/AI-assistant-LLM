from elevenlabs.client import ElevenLabs
from elevenlabs import play
_11 = ElevenLabs(api_key="sk_6aea8b24cef93bd18a8c965c8486e39d85076ee9c32661a1")
#female: hkfHEbBvdQFNX4uWHqRF
#male: fQj4gJSexpu8RDE2Ii5m
VOICE_ID  = "hkfHEbBvdQFNX4uWHqRF" 
MODEL_ID  = "eleven_multilingual_v2"
BASE_SETTINGS   = {"stability": 0.95, "similarity_boost": 0.8, "speed": 1.0}

def speak(text: str, mute: bool = False):
    speed = 1.2 if len(text) > 25 else 1.0
    voice_settings = BASE_SETTINGS | {"speed": speed}
    audio = _11.text_to_speech.convert(
        text=text,
        voice_id=VOICE_ID,
        model_id=MODEL_ID,
        output_format="mp3_44100_128",
        voice_settings=voice_settings
    )
    if not mute:
        play(audio)       
    return audio 