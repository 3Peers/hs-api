from rest_framework import generics, pagination
from rest_framework.permissions import IsAuthenticated
from entities.models import Job, JobApplication
from entities.serializers import JobSerializer, JobApplicationSerializer


class JobCreateListView(generics.ListCreateAPIView):
    queryset = Job.get_all()
    serializer_class = JobSerializer
    pagination_class = pagination.PageNumberPagination
    permission_classes = (IsAuthenticated,)


class JobRUDView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    queryset = Job.get_all()
    serializer_class = JobSerializer
    permission_classes = (IsAuthenticated,)

    def perform_destroy(self, instance):
        if self.request.user and self.request.user.is_superuser():
            super().perform_destroy(instance)


class JobApplicationCreateListView(generics.ListCreateAPIView):
    queryset = JobApplication.get_all()
    serializer_class = JobApplicationSerializer
    pagination_class = pagination.PageNumberPagination
    permission_classes = (IsAuthenticated,)


class JobApplicationRUDView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'pk'
    queryset = JobApplication.get_all()
    serializer_class = JobApplicationSerializer
    permission_classes = (IsAuthenticated,)

    def perform_destroy(self, instance):
        if self.request.user and JobApplication.is_users_job_application(self.request.user, instance) \
            and self.request.user.is_superuser():
            super().perform_destroy(instance)
