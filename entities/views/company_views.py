from rest_framework import generics, pagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from entities.models import Company
from entities.serializers import CompanySerializer


class CompanyCreateListView(generics.ListCreateAPIView):
    queryset = Company.get_all()
    serializer_class = CompanySerializer
    pagination_class = pagination.PageNumberPagination
    permission_classes = (IsAuthenticated,)


class CompanyRUDView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    queryset = Company.get_all()
    serializer_class = CompanySerializer
    permission_classes = (IsAuthenticated,)

    def perform_destroy(self, instance):
        if self.request.user and self.request.user.is_admin:
            return super().perform_destroy(instance)
        raise PermissionDenied('You are not allowed to perform this action.')