import time
from django.shortcuts import render
from .weather_service import WeatherService


def weather_widget(request):
    # 지연 파라미터 처리 (테스트 목적)
    delay = request.GET.get("delay", 0)
    try:
        delay = float(delay)
        if 0 < delay <= 5:  # 최대 5초로 제한
            time.sleep(delay)
    except (ValueError, TypeError):
        pass  # 잘못된 값은 무시

    weather_service = WeatherService()

    # 서울의 고정된 좌표 사용
    seoul_lat = 37.5665
    seoul_lon = 126.9780

    # 날씨 데이터 가져오기
    weather_data = weather_service.get_weather(seoul_lat, seoul_lon, "서울")

    context = {
        "weather": weather_data,
    }

    # HTMX 요청인 경우 부분 템플릿 반환
    if request.headers.get("HX-Request"):
        return render(request, "widgets/weather/weather_widget.html", context)

    # 일반 요청인 경우에도 동일한 템플릿 반환 (weather_page.html이 없으므로)
    return render(request, "widgets/weather/weather_widget.html", context)
