import random
from datetime import datetime
from django.core.cache import cache
from django.utils import timezone


class WeatherService:
    CACHE_DURATION = 600  # 10 minutes in seconds
    
    # 날씨 상태 옵션
    WEATHER_CONDITIONS = [
        ("맑음", "01d"),
        ("구름 조금", "02d"),
        ("흐림", "03d"),
        ("비", "10d"),
        ("천둥번개", "11d"),
        ("눈", "13d"),
        ("안개", "50d"),
    ]

    def get_weather(self, lat, lon, location_name=None):
        cache_key = f"weather_{lat}_{lon}"
        
        # 캐시 체크 (선택사항 - 더 동적인 데이터를 원하면 주석 처리)
        # cached_data = cache.get(cache_key)
        # if cached_data:
        #     return cached_data
        
        # 랜덤 날씨 데이터 생성
        weather_data = self.generate_random_weather(location_name)
        
        # 캐시 저장 (선택사항)
        # cache.set(cache_key, weather_data, self.CACHE_DURATION)
        
        return weather_data

    def generate_random_weather(self, location_name=None):
        # 랜덤 날씨 상태 선택
        condition, icon = random.choice(self.WEATHER_CONDITIONS)
        
        # 기온 생성 (계절감 있게)
        base_temp = random.uniform(15, 30)
        temp = round(base_temp + random.uniform(-2, 2), 1)
        feels_like = round(temp + random.uniform(-2, 3), 1)
        temp_min = round(temp - random.uniform(2, 5), 1)
        temp_max = round(temp + random.uniform(2, 5), 1)
        
        # 습도와 풍속
        humidity = random.randint(30, 90)
        wind_speed = round(random.uniform(0, 10), 1)
        
        # 일출/일몰 시간 (고정값에 약간의 변화)
        now = datetime.now()
        sunrise_hour = 6 + random.randint(-30, 30) // 60
        sunrise_minute = random.randint(0, 59)
        sunset_hour = 18 + random.randint(-30, 30) // 60
        sunset_minute = random.randint(0, 59)
        
        return {
            "location": location_name or "서울",
            "temp": temp,
            "feels_like": feels_like,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "description": condition,
            "icon": icon,
            "sunrise": now.replace(hour=sunrise_hour, minute=sunrise_minute),
            "sunset": now.replace(hour=sunset_hour, minute=sunset_minute),
            "updated_at": timezone.now(),
            "is_dummy": True,  # 더미 데이터임을 표시
        }

    def get_default_weather(self, location_name=None):
        # 기존 메서드와의 호환성을 위해 유지
        return self.generate_random_weather(location_name)