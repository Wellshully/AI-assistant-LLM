import requests
from datetime import datetime,timedelta

API_KEY = "CWA-9544C8F6-2267-4106-8246-78B0980BE9CB"
location_name = "臺北市"
target_area = "內湖區"

def fetch_weather():
    url = (
        f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-061"
        f"?Authorization={API_KEY}"
        f"&format=JSON"
        f"&locationName={location_name}"
    )
    r = requests.get(url,verify=False)
    r.raise_for_status()
    return r.json()

def parse_today_weather(data):
    now = datetime.now()
    today = now.date()
    if now.hour >= 20:
        today += timedelta(days=1)
    location_list = data['records']['Locations'][0]['Location']
    # 修正大小寫
    target_location = next((loc for loc in location_list if loc['LocationName'] == target_area), None)
    if not target_location:
        return f"找不到 {target_area} 的資料"

    weather_elements = target_location['WeatherElement']

    weather_descs = []
    temps = []

    for elem in weather_elements:
        if elem['ElementName'] == '天氣預報綜合描述':
            for time_slot in elem['Time']:
                start_time = datetime.fromisoformat(time_slot['StartTime'][:-6])
                if start_time.date() == today:
                    desc = time_slot['ElementValue'][0]['WeatherDescription']
                    weather_descs.append(desc)

        if elem['ElementName'] == '溫度':
            for time_slot in elem['Time']:
                data_time = datetime.fromisoformat(time_slot['DataTime'][:-6])
                if data_time.date() == today:
                    temp = int(time_slot['ElementValue'][0]['Temperature'])
                    temps.append(temp)

    temp_min, temp_max = (min(temps), max(temps)) if temps else (None, None)

    return {
        "區域": target_area,
        "日期": today.isoformat(),
        "天氣描述": weather_descs,
        "溫度範圍": (temp_min, temp_max)
    }
if __name__ == "__main__":
    data = fetch_weather()
    result = parse_today_weather(data)
    print(result)
