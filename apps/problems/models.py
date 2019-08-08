from django.db import models
from apps.assessments.models import Assessment
from apps.user.models import User


class Problem(models.Model):
    '''visibility_time is the time for which the problem is visible to the user
    '''

    max_score = models.FloatField()
    assessment = models.ForeignKey(Assessment, null=True, on_delete=models.SET_NULL)
    visibility_time = models.FloatField()
    negative_score = models.IntegerField(default=0)
    title = models.CharField(max_length=50)
    description = models.TextField(null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class McqProblem(Problem):
    multiple_correct = models.BooleanField(default=False)
    is_partial = models.BooleanField(default=False)


class McqOption(models.Model):
    problem = models.ForeignKey(McqProblem, on_delete=models.CASCADE, related_name='options')
    is_correct = models.BooleanField(default=False)
    score = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class McqSubmission(models.Model):
    '''User has chosen `option` as correct answer for `problem` related to `option's` `problem`
    '''

    submitter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='options')
    option = models.ForeignKey(McqOption, on_delete=models.PROTECT,
                               related_name='correct_submissions')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
