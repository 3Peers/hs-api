from django.urls import path
from .views import (
    UserListCreateView,
    UserRetrieveDeleteView,
    GetCurrentUserView,
    SendOTPView,
    VerifyOTPView
)

urlpatterns = [
    path('', UserListCreateView.as_view(), name='list_and_create'),
    path('me/', GetCurrentUserView.as_view(), name='get_current_user'),
    path('sign-up/send-otp/', SendOTPView.as_view(), name='send_otp_view'),
    path('sign-up/verify-otp/', VerifyOTPView.as_view(), name='verify_otp_view'),
    path('<int:pk>/', UserRetrieveDeleteView.as_view(), name='get_and_delete')
]
