from rest_framework import generics, pagination
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from entities.models import Profession
from entities.serializers import ProfessionSerializer


class ProfessionCreateListView(generics.ListCreateAPIView):
    queryset = Profession.get_all()
    serializer_class = ProfessionSerializer
    pagination_class = pagination.PageNumberPagination
    permission_classes = (IsAuthenticated,)


class ProfessionRUDView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    queryset = Profession.get_all()
    serializer_class = ProfessionSerializer
    permission_classes = (IsAuthenticated,)

    def perform_destroy(self, instance):
        if self.request.user and self.request.user.is_admin:
            return super().perform_destroy(instance)
        raise PermissionDenied('You are not allowed to perform this action.')