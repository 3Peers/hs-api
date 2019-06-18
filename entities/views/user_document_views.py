from rest_framework import generics, pagination
from rest_framework.permissions import IsAuthenticated
from entities.models import UserDocument
from entities.serializers import UserDocumentSerializer



class UserDocumentCreateListView(generics.ListCreateAPIView):
    queryset = UserDocument.get_all()
    serializer_class = UserDocumentSerializer
    pagination_class = pagination.PageNumberPagination
    permission_classes = (IsAuthenticated,)


class UserDocumentRUDView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    queryset = UserDocument.get_all()
    serializer_class = UserDocumentSerializer
    permission_classes = (IsAuthenticated,)

    def perform_destroy(self, instance):
        if UserDocument.is_users_document(self.request.user, instance) \
            or self.request.user.is_admin():
            return super().perform_destroy(instance)