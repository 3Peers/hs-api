from django.urls import path
from .views import CreateAssessmentView


urlpatterns = [
    path('create/', CreateAssessmentView.as_view(), name='create-assessment')
]
