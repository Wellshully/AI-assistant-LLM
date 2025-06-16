import sounddevice as sd

for i, dev in enumerate(sd.query_devices()):
    if dev["max_input_channels"] > 0:
        print(
            f"Device {i}: {dev['name']} - Input Channels: {dev['max_input_channels']}"
        )
