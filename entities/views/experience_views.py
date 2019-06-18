from rest_framework import generics, pagination
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from entities.models import Experience
from user.models import User
from entities.serializers import ExperienceSerializer


class UserExperienceCreateListView(generics.ListCreateAPIView):
    serializer_class = ExperienceSerializer
    pagination_class = pagination.PageNumberPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Experience.get_user_experiences(user_id)
    
    def perform_create(self, serializer):
        user_id = self.kwargs.get('user_id')

        if self.request.user and self.request.user.id == user_id:
            serializer.validated_data['user'] = self.request.user
            return super().perform_create(serializer)
        raise PermissionDenied('You are not allowed to perform this action.')

class UserExperienceRUDView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    serializer_class = ExperienceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Experience.get_user_experiences(user_id)
    
    def perform_destroy(self, instance):
        if self.request.user and self.request.user.is_admin:
            return super().perform_destroy(instance)
        raise PermissionDenied('You are not allowed to perform this action.')