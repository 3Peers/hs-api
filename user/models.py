from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    about = models.TextField(default='', blank=True)
    primary_phone_no = models.CharField(max_length=15, null=True)
    secondary_phone_no = models.CharField(max_length=15, null=True)
    secondary_email = models.EmailField(null=True)
    profile_picture = models.URLField(null=True)
    address = models.TextField(null=True)
    city = models.CharField(max_length=30, null=True)
    state = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def get_all_users():
        return User.objects.all()

    def __str__(self):
        return self.username
