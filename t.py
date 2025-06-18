import sounddevice as sd
import numpy as np

duration = 2  # seconds
samplerate = 16000

print("Recording...")
audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
sd.wait()
print("Done.")