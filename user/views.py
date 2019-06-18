from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from .models import User
from .serializers import UserSerializer


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.get_all_users()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination


class UserRetrieveDeleteView(generics.RetrieveDestroyAPIView):
    lookup_field = 'pk'
    queryset = User.get_all_users()
    serializer_class = UserSerializer