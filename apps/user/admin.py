from django.contrib import admin
from .models import User, AuthOTP


admin.site.register([User, AuthOTP])
