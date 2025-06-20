import asyncio, threading, queue, time
from bleak import BleakClient

_RETRY_SEC = 3         

class BLEWorker:
    def __init__(self, mac, char_uuid):
        self.mac = mac
        self.char_uuid = char_uuid
        self._q = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=False)
        self._thread.start()

    # ---------- public ----------
    def light_on(self):  self._q.put(("light", True))
    def light_off(self): self._q.put(("light", False))
    def stop(self):      self._q.put(("__stop__", None)); self._thread.join(2)

    # ---------- private ----------
    def _run(self):
        asyncio.run(self._loop())

    async def _loop(self):
        while True:
            cmd, arg = await asyncio.to_thread(self._q.get)
            if cmd == "__stop__":
                print("[BLE] closing...")
                break
            try:
                async with BleakClient(self.mac) as client:
                    if cmd == "light":
                        data = bytearray([0x57, 0x01, 0x01 if arg else 0x02])
                        await client.write_gatt_char(self.char_uuid, data)
            except Exception as e:
                print("[BLE ERROR]", e)
                await asyncio.sleep(2)
