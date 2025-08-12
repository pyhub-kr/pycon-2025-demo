from django.shortcuts import render
from .weather_service import WeatherService

def weather_widget(request):
    weather_service = WeatherService()

    # 서울의 고정된 좌표 사용
    seoul_lat = 37.5665
    seoul_lon = 126.9780

    # 날씨 데이터 가져오기
    weather_data = weather_service.get_weather(seoul_lat, seoul_lon, "서울")

    context = {"weather": weather_data}
    return render(request, "widgets/weather/weather_widget.html", context)
