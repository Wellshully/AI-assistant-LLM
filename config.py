# config.py

# 語音與語音生成設定
ELE_API = "sk_6aea8b24cef93bd18a8c965c8486e39d85076ee9c32661a1"
VOICE_ID = "hkfHEbBvdQFNX4uWHqRF"
MODEL_ID = "eleven_flash_v2_5"
BASE_SETTINGS = {"stability": 0.95, "similarity_boost": 0.85, "speed": 1.0}
CACHE_DIR = "tts_cache"

# Gemini client 設定
GEMINI_API = "AIzaSyDEwTDG5ul6RGCoVIamkn7FtCfm4XFOAX8"
# 語音辨識與語音控制
DEVICE_ID = 5
SAMPLE_RATE = 16000
MODEL_PATH = "models/vosk-model-small-en-us-0.15"

# 語音指令對應表
CMD_MAP = {
    "light up": "on_light",
    "light on": "on_light",
    "light off": "off_light",
    "like of": "off_light",
    "hey turn off light": "off_light",
    "hey like off": "off_light",
    "hey light of": "off_light",
    "hey night of": "off_light",
    "hey night oof": "off_light",
    "hey laid off": "off_light",
    "hey light off": "off_light",
    "hey lied off": "off_light",
    "hey turn on light": "on_light",
    "hey like oh": "on_light",
    "hey lied on": "on_light",
    "hey light on": "on_light",
    "hey night on": "on_light",
    "hey like on": "on_light",
    "hey light up": "on_light",
    "hey shut down my pc": "pc_off",
    "hey listen": "llm",
    "hey open mail": "open_mail",
    "hey open cs": "open_cs",
    "hey open seas": "open_cs",
    "hey play rock": "play_rock",
    "hey open you tube": "open_youtube",
    "hey open you too": "open_youtube",
    "hey weather": "weather",
    "hey pass": "type_pass",
}

# 語意與語音參數
MAX_WORDS = 120
MAX_TOKENS = 150
THRESHOLD = 90
LANG = "zh-TW"
SEC_RECORD = 5
MEMORY_PATH = "memory.json"
MAX_SIZE = 5 * 1024 * 1024

# 網路與遠端設定
REMOTE_USER = "welly"
REMOTE_HOST = "192.168.66.14"
BOT_MAC = "EE:2E:05:86:36:8D"
WRITE_CHAR_UUID = "cba20002-224d-11e6-9fb8-0002a5d5c51b"
PASS = "Zxc9249258852xc"

# 天氣
WEA_API = "CWA-9544C8F6-2267-4106-8246-78B0980BE9CB"
location_name = "臺北市"
target_area = "內湖區"
