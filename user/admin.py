from django.contrib import admin
from .models import User, SignUpOTP


admin.site.register([User, SignUpOTP])
