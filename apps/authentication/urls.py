from django.urls import path
from .views import ResetPasswordView, ForgotPasswordView, RegisterUserView, LoginUserView

urlpatterns = [
    path('api/auth/login/', LoginUserView.as_view(), name='token_obtain_pair'),
    path('api/auth/forgot_password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('api/auth/register/', RegisterUserView.as_view(), name='register_user'),
    path('api/auth/forgot_password/reset/', ResetPasswordView.as_view(), name='reset_password'),
]