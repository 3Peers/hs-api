from django.urls import path
from .views import (ProfessionCreateListView, ProfessionRUDView,
                    CompanyCreateListView, CompanyRUDView,
                    UserExperienceCreateListView, UserExperienceRUDView,
                    UserEducationCreateListView, UserEducationRUDView,
                    UserDocumentCreateListView, UserDocumentRUDView,
                    JobApplicationCreateListView, JobApplicationRUDView,
                    JobCreateListView, JobRUDView)


urlpatterns = [
    path('profession/', ProfessionCreateListView.as_view(), name='profession-cl'),
    path('profession/<int:pk>/', ProfessionRUDView.as_view(), name='profession-rud'),

    path('company/', CompanyCreateListView.as_view(), name='company-cl'),
    path('company/<int:pk>/', CompanyRUDView.as_view(), name='company-rud'),

    path('user/<int:user_id>/experience/', UserExperienceCreateListView.as_view(),
         name='experience-cl'),
    path('user/<int:user_id>/experiece/<int:pk>/', UserExperienceRUDView.as_view(),
         name='experience-rud'),

    path('user/<int:user_id>/education/', UserEducationCreateListView.as_view(),
         name='education-cl'),
    path('user/<int:user_id>/education/<int:pk>/', UserEducationRUDView.as_view(),
         name='education-rud'),

    path('user-document/', UserDocumentCreateListView.as_view(), name='user-document-cl'),
    path('user-document/<int:pk>/', UserDocumentRUDView.as_view(), name='user-document-rud'),

    path('job-application/', JobApplicationCreateListView.as_view(), name='job-application-cl'),
    path('job-application/<int:pk>/', JobApplicationRUDView.as_view(),
         name='job-application-rud'),

    path('job/', JobCreateListView.as_view(), name='job-cl'),
    path('job/<int:pk>/', JobRUDView.as_view(), name='job-rud')
]
