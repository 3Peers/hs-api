from django.db import models
from user.models import User


class Skill(models.Model):
    name = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Profession(models.Model):
    name = models.CharField(max_length=30, blank=False)
    industry = models.CharField(max_length=30, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_all(cls):
        return cls.objects.all()


class Company(models.Model):
    name = models.CharField(max_length=100, blank=False)
    established_on = models.DateField()
    about = models.TextField(blank=False)
    industry = models.CharField(max_length=50, blank=False)
    logo = models.URLField(null=True)
    size = models.IntegerField()
    website = models.URLField(null=True)
    phone = models.CharField(max_length=20)
    headquarters = models.CharField(max_length=50)
    type = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_all(cls):
        return cls.objects.all()


class Experience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='professions')
    profession = models.ForeignKey(Profession, on_delete=models.PROTECT,
                                   related_name='holders_history')
    start_date = models.DateField(blank=False)
    end_date = models.DateField(null=True)
    description = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @staticmethod
    def get_user_experiences(user_id):
        return Experience.objects.filter(user__id=user_id)


class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='education')
    degree = models.CharField(max_length=100, blank=False)
    field = models.CharField(max_length=100, blank=False)
    institute = models.CharField(max_length=200, blank=False)
    grade = models.CharField(max_length=15, default='')
    start_date = models.DateField(blank=False)
    end_date = models.DateField(null=True)
    extra_activities = models.TextField(default='')
    description = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @staticmethod
    def get_user_education(user_id):
        return Education.objects.filter(user__id=user_id)

    @staticmethod
    def is_users_education(user: User, education_instance):
        return education_instance.user == user


class UserDocument(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    experience = models.ForeignKey(Experience, on_delete=models.CASCADE, null=True,
                                   related_name='related_documents')
    education = models.ForeignKey(Education, on_delete=models.CASCADE, null=True,
                                  related_name='related_documents')
    document = models.FileField(null=False)
    doc_type = models.CharField(max_length=15, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def save_document(cls, user_document,
                      experience: Experience = None,
                      education: Education = None):
        user_document.experience = experience
        user_document.education = education
        return user_document.save()

    @staticmethod
    def is_users_document(user: User, user_document):
        return user_document.owner == user


class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True, related_name='jobs')
    profession = models.ForeignKey(Profession, on_delete=models.PROTECT,
                                   null=True, related_name='jobs')
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs_posted')
    assessment_based = models.BooleanField(default=False)
    description = models.TextField(blank=False)
    end_date = models.DateTimeField()
    location = models.CharField(max_length=100)
    open_to_all = models.BooleanField(default=False)
    employment_type = models.CharField(max_length=100)
    seniority_level = models.CharField(max_length=100)
    skills_required = models.ManyToManyField(Skill)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_all(cls):
        return cls.objects.all()


class JobApplication(models.Model):
    # TODO: Should this be CASCADED on job deletion?
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                                  related_name='jobs_applied_for')
    status = models.CharField(max_length=20)
    withdrawn = models.BooleanField(default=False)
    feedback = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @staticmethod
    def is_users_job_application(user: User, job_application):
        return job_application.applicant == user
