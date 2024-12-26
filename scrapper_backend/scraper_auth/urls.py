from django.urls import path
from .views import (
    SignUpView, VerifyOTPView, LoginView,
    PasswordResetRequestView, PasswordResetConfirmView
)

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]