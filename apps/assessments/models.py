from django.db import models
from apps.entities.models import Job


class Assessment(models.Model):
    name = models.CharField(max_length=100, blank=False)
    logo = models.URLField()
    job = models.ForeignKey(Job, null=True, on_delete=models.SET_NULL, related_name='assessments')
    description = models.TextField(blank=False)
    rules = models.TextField(blank=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
