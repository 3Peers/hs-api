from rest_framework import generics, pagination
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from entities.models import Education
from user.models import User
from entities.serializers import EducationSerializer


class UserEducationCreateListView(generics.ListCreateAPIView):
    serializer_class = EducationSerializer
    pagination_class = pagination.PageNumberPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Education.get_user_education(user_id)

    def perform_create(self, serializer):
        user_id = self.kwargs.get('user_id')

        if self.request.user and self.request.user.id == user_id:
            serializer.validated_data['user'] = self.request.user
            return super().perform_create(serializer)
        raise PermissionDenied('You are not allowed to perform this action.')


class UserEducationRUDView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    serializer_class = EducationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return Education.get_user_experiences(user_id)
    
    def perform_destroy(self, instance):
        if Education.is_users_education(instance, self.request.user) \
            or self.request.user.is_admin():
            return super().perform_destroy(instance)
