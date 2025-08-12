from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from datetime import timedelta
import json
import random


# 기본 admin site를 확장
original_get_urls = admin.site.get_urls


def get_urls():
    def api_statistics_data(request):
        """통계 데이터를 JSON으로 반환하는 API"""
        now = timezone.now()
        
        # 실시간 데이터 시뮬레이션 (실제로는 DB에서 가져와야 함)
        daily_stats = []
        for i in range(6, -1, -1):
            date = now - timedelta(days=i)
            daily_stats.append({
                'date': date.strftime('%m/%d'),
                'views': random.randint(80, 150),  # 실시간 효과를 위한 랜덤 데이터
                'users': random.randint(15, 40),
            })
        
        monthly_stats = []
        for i in range(5, -1, -1):
            date = now - timedelta(days=i*30)
            monthly_stats.append({
                'month': date.strftime('%Y년 %m월'),
                'views': random.randint(2800, 3500),
                'users': random.randint(550, 700),
            })
        
        data = {
            'daily_stats': daily_stats,
            'monthly_stats': monthly_stats,
            'total_users': User.objects.count(),
            'active_users_today': User.objects.filter(
                last_login__gte=now - timedelta(days=1)
            ).count(),
            'timestamp': now.isoformat(),
        }
        
        return JsonResponse(data)
    
    def api_statistics_cards(request):
        """통계 카드 부분만 반환하는 HTMX partial view"""
        now = timezone.now()
        context = {
            'total_users': User.objects.count(),
            'active_users_today': User.objects.filter(
                last_login__gte=now - timedelta(days=1)
            ).count(),
            'page_views_week': random.randint(1000, 2000),
            'avg_response_time': round(random.uniform(0.08, 0.15), 2),
        }
        return TemplateResponse(request, 'admin/partials/statistics_cards.html', context)
    
    def api_user_activity_data(request):
        """사용자 활동 데이터를 JSON으로 반환하는 API"""
        now = timezone.now()
        
        recent_users = list(User.objects.order_by('-date_joined')[:10].values(
            'id', 'username', 'email', 'date_joined'
        ))
        
        recent_logins = list(User.objects.filter(
            last_login__isnull=False
        ).order_by('-last_login')[:10].values(
            'id', 'username', 'email', 'last_login'
        ))
        
        # 날짜를 문자열로 변환
        for user in recent_users:
            user['date_joined'] = user['date_joined'].isoformat()
        for user in recent_logins:
            user['last_login'] = user['last_login'].isoformat()
        
        data = {
            'recent_users': recent_users,
            'recent_logins': recent_logins,
            'online_users': User.objects.filter(
                last_login__gte=now - timedelta(minutes=5)
            ).count(),
            'total_users': User.objects.count(),
            'timestamp': now.isoformat(),
        }
        
        return JsonResponse(data)
    
    def api_user_activity_list(request):
        """사용자 활동 목록 부분만 반환하는 HTMX partial view"""
        now = timezone.now()
        list_type = request.GET.get('type', 'login')
        
        if list_type == 'login':
            users = User.objects.filter(
                last_login__isnull=False
            ).order_by('-last_login')[:10]
            title = '최근 로그인 사용자'
        else:
            users = User.objects.order_by('-date_joined')[:10]
            title = '최근 가입 사용자'
        
        context = {
            'users': users,
            'list_type': list_type,
            'title': title,
        }
        return TemplateResponse(request, 'admin/partials/user_activity_list.html', context)
    
    def statistics_view(request):
        context = dict(
            admin.site.each_context(request),
            title='실시간 통계 대시보드',
        )
        
        # 샘플 통계 데이터 생성
        now = timezone.now()
        
        # 일별 통계 (최근 7일)
        daily_stats = []
        for i in range(6, -1, -1):
            date = now - timedelta(days=i)
            daily_stats.append({
                'date': date.strftime('%m/%d'),
                'views': 100 + (i * 10),  # 샘플 데이터
                'users': 20 + (i * 2),     # 샘플 데이터
            })
        
        # 월별 통계 (최근 6개월)
        monthly_stats = []
        for i in range(5, -1, -1):
            date = now - timedelta(days=i*30)
            monthly_stats.append({
                'month': date.strftime('%Y년 %m월'),
                'views': 3000 + (i * 100),
                'users': 600 + (i * 20),
            })
        
        context.update({
            'daily_stats': json.dumps(daily_stats),
            'monthly_stats': json.dumps(monthly_stats),
            'total_users': User.objects.count(),
            'active_users_today': User.objects.filter(
                last_login__gte=now - timedelta(days=1)
            ).count(),
        })
        
        return TemplateResponse(request, 'admin/statistics.html', context)
    
    def user_activity_view(request):
        context = dict(
            admin.site.each_context(request),
            title='사용자 활동 모니터링',
        )
        
        now = timezone.now()
        
        # 최근 가입한 사용자
        recent_users = User.objects.order_by('-date_joined')[:10]
        
        # 최근 로그인한 사용자
        recent_logins = User.objects.filter(
            last_login__isnull=False
        ).order_by('-last_login')[:10]
        
        # 온라인 사용자 (최근 5분 이내 활동)
        online_users = User.objects.filter(
            last_login__gte=now - timedelta(minutes=5)
        ).count()
        
        context.update({
            'recent_users': recent_users,
            'recent_logins': recent_logins,
            'online_users': online_users,
            'total_users': User.objects.count(),
        })
        
        return TemplateResponse(request, 'admin/user_activity.html', context)
    
    urls = original_get_urls()
    custom_urls = [
        # 페이지 뷰
        path('statistics/', admin.site.admin_view(statistics_view), name='admin_statistics'),
        path('user-activity/', admin.site.admin_view(user_activity_view), name='admin_user_activity'),
        # API 엔드포인트
        path('api/statistics/data/', admin.site.admin_view(api_statistics_data), name='admin_api_statistics_data'),
        path('api/statistics/cards/', admin.site.admin_view(api_statistics_cards), name='admin_api_statistics_cards'),
        path('api/user-activity/data/', admin.site.admin_view(api_user_activity_data), name='admin_api_user_activity_data'),
        path('api/user-activity/list/', admin.site.admin_view(api_user_activity_list), name='admin_api_user_activity_list'),
    ]
    return custom_urls + urls


# admin site의 get_urls 메서드를 패치
admin.site.get_urls = get_urls

# Admin 헤더 커스터마이징
admin.site.site_header = 'Django Admin 커스터마이징 예시'
admin.site.site_title = 'Admin'
admin.site.index_title = '관리자 대시보드'
