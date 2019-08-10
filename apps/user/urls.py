from django.urls import path
from .views import (
    UserRetrieveView,
    GetCurrentUserView,
    SignUpSendOTPView,
    ForgotPasswordSendOTPView,
    VerifyOTPView,
    ChangePasswordView,
    CheckUserExistsView

)

urlpatterns = [
    path('me/', GetCurrentUserView.as_view(), name='get_current_user'),
    path('exists/', CheckUserExistsView.as_view(), name='check_user_exists_view'),
    path('forgot-password/', ForgotPasswordSendOTPView.as_view(), name='forgot_password_view'),
    path('sign-up/', SignUpSendOTPView.as_view(), name='sign_up_view'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp_view'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('<int:pk>/', UserRetrieveView.as_view(), name='get_user_view')
]
