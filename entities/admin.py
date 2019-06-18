from django.contrib import admin
from .models import (Profession, Company, Experience,
    Education, UserDocument, Skill, Job, JobApplication)

admin.site.register([Profession, Company, Experience,
    Education, UserDocument, Skill, Job, JobApplication])