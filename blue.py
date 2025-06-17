import asyncio
from bleak import BleakClient

DEVICE_MAC = "EE:2E:05:86:36:8D"  # 你剛剛掃到的 MAC 地址
WRITE_CHAR_UUID = "cba20002-224d-11e6-9fb8-0002a5d5c51b"  # 固定的 UUID

async def press_bot():
    async with BleakClient(DEVICE_MAC) as client:
        if await client.is_connected():
            print("✅ Connected to SwitchBot Bot")
            # 按一下
            await client.write_gatt_char(WRITE_CHAR_UUID, bytearray([0x57, 0x01, 0x01]))
            print("🔘 Sent press command")
        else:
            print("❌ Failed to connect")

asyncio.run(press_bot())