from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    # 회원가입
    path("signup/", views.SignupView.as_view(), name="signup"),
    # 로그인/로그아웃
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    # 프로필
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    # 비밀번호 변경
    path("password_change/", views.CustomPasswordChangeView.as_view(), name="password_change"),
    path("password_change/done/", views.CustomPasswordChangeDoneView.as_view(), name="password_change_done"),
    # 비밀번호 재설정
    path("password_reset/", views.CustomPasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", views.CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", views.CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", views.CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
