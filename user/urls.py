from django.urls import path
from .views import UserListCreateView, UserRetrieveDeleteView


urlpatterns = [
    path('', UserListCreateView.as_view(), name='list_and_create'),
    path('<int:pk>/', UserRetrieveDeleteView.as_view(), name='get_and_delete')
]