import asyncio
from aiohttp import ClientSession
from thinqconnect.thinq_api import ThinQApi, ThinQAPIException
import config
import uuid
import json
from typing import Optional, Dict, Any
from thinqconnect.devices.air_conditioner import AirConditionerDevice
client_id = str(uuid.uuid4())
DEVICE_ID = config.LG_DEVICE_ID
ACCESS_TOKEN=config.LG_ACCESS_TOKEN
COUNTRY_CODE=config.COUNTRY_CODE
_POLL_INTERVAL = 1.0     
_POLL_RETRY    = 6  
async def _api() -> ThinQApi:
    sess = ClientSession()
    return ThinQApi(sess, access_token=ACCESS_TOKEN, country_code=COUNTRY_CODE)
async def _post(api: ThinQApi, payload: Dict[str, Any]):
    await api.async_set_device_controls(DEVICE_ID, payload)
    print("✅ sent:", payload)

async def _status(api: ThinQApi) -> Dict[str, Any]:
    return await api.async_get_device_status(DEVICE_ID)

async def _is_power_on(api: ThinQApi) -> bool:
    return (await _status(api))["operation"]["airConOperationMode"] == "POWER_ON"

async def _post(api: ThinQApi, payload: Dict[str, Any]):
    await api.async_post_device_control(DEVICE_ID, payload)
    print("✅ sent:", payload)

async def ac_set(
    *,
    power: Optional[bool] = None,       # True=on, False=off, None=not changed
    mode:  Optional[str]  = None,       # "COOL" "HEAT" "AIR_DRY" "AUTO" "FAN"
    temp:  Optional[float] = None,      # 18–30°C, 0.5 step
    fan:   Optional[str]  = None        # "LOW" "MID" "HIGH" "AUTO"
) -> None:
    async with ClientSession() as sess:
        api = ThinQApi(
            session=sess,
            access_token=ACCESS_TOKEN,
            country_code=COUNTRY_CODE,
            client_id=str(uuid.uuid4()),
        )

        profile = await api.async_get_device_profile(DEVICE_ID)
        ac = AirConditionerDevice(
            thinq_api=api,
            device_id=DEVICE_ID,
            device_type="DEVICE_AIR_CONDITIONER",
            model_name="",
            alias="",
            reportable=True,
            profile=profile,
        )

        try:
            # 1) power
            if power is True:
                await ac.set_air_con_operation_mode("POWER_ON")
                await asyncio.sleep(1)
            elif power is False:
                await ac.set_air_con_operation_mode("POWER_OFF")
                return
            # 2) mode
            if mode:
                await ac.set_current_job_mode(mode)

            # 3) temp
            if temp is not None:
                if mode == "COOL":
                    await ac.set_cool_target_temperature_c(temp)
                    
                elif mode == "HEAT":
                    await ac.set_heat_target_temperature_c(temp)
                elif mode == "AUTO":
                    await ac.set_auto_target_temperature_c(temp)
                else:  # FAN / AIR_DRY 也可用一般 target
                    await ac._set_target_temperature(temp, "C")
                await asyncio.sleep(1)
            # 4) fan
            if fan:
                await ac.set_wind_strength(fan)
                await asyncio.sleep(1)

            print("✅ ac_set 完成")
        except ThinQAPIException as exc:
            print(f"❌ ThinQ 例外 {exc.code}: {exc.message}")
async def print_pm25_and_filter():
    async with ClientSession() as sess:
        api = ThinQApi(
            session=sess,
            access_token=ACCESS_TOKEN,
            country_code=COUNTRY_CODE,
            client_id=str(uuid.uuid4()),
        )

        status = await api.async_get_device_status(DEVICE_ID)

        pm25   = status["airQualitySensor"]["PM2"]            # μg/m³
        remain = status["filterInfo"]["filterRemainPercent"]  # %

        print(f"🏷  PM2.5  : {pm25} µg/m³")
        print(f"🏷  濾網壽命: {remain}%")
async def dump_status():
    async with ClientSession() as sess:
        api = ThinQApi(sess, access_token=ACCESS_TOKEN,
                       country_code=COUNTRY_CODE,
                       client_id=str(uuid.uuid4()))
        status = await api.async_get_device_status(DEVICE_ID)
        print(json.dumps(status, indent=2, ensure_ascii=False))

#asyncio.run(dump_status())
#asyncio.run(print_pm25_and_filter())
#asyncio.run(ac_set(mode="COOL", temp=27, fan="LOW"))
asyncio.run(dump_status())
