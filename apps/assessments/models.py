from django.db import models
from apps.entities.models import Job
from apps.user.models import User

from .constants import AssessmentTypes


class Assessment(models.Model):
    creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='assessments')
    name = models.CharField(max_length=100, blank=False)
    type = models.CharField(max_length=100, choices=AssessmentTypes.get_choices())
    logo = models.URLField()
    banner_image = models.URLField()
    job = models.ForeignKey(Job, null=True, on_delete=models.SET_NULL, related_name='assessments')
    description = models.TextField(blank=False)
    is_online = models.BooleanField(default=True)
    rules = models.TextField(blank=False)
    min_team_size = models.IntegerField(default=1)
    max_team_size = models.IntegerField(default=1)
    active = models.BooleanField(default=True)
    public = models.BooleanField(default=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
