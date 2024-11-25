from django.db import models

# Create your models here.
from django.db import models


class JiraIssue(models.Model):
    summary = models.CharField(max_length=500)
    key = models.CharField(max_length=20, unique=True)
    issue_type = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    assignee = models.CharField(max_length=100)
    created_date = models.DateTimeField()
    updated_date = models.DateTimeField()
    resolved_date = models.DateTimeField(null=True, blank=True)
    story_points = models.FloatField(null=True)
    time_spent = models.IntegerField(default=0)  # en segundos
    sprint = models.CharField(max_length=100, null=True)
    quarter = models.CharField(max_length=20)
    project = models.CharField(max_length=100)

    class Meta:
        indexes = [
            models.Index(fields=['assignee']),
            models.Index(fields=['created_date']),
            models.Index(fields=['status']),
            models.Index(fields=['sprint'])
        ]

    def time_spent_hours(self):
        return round(self.time_spent / 3600, 2)


class SprintMetrics(models.Model):
    sprint = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_points = models.FloatField(default=0)
    completed_points = models.FloatField(default=0)
    total_issues = models.IntegerField(default=0)
    completed_issues = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['sprint']),
            models.Index(fields=['start_date'])
        ]

    @property
    def completion_rate(self):
        return round((self.completed_points / self.total_points * 100), 2) if self.total_points > 0 else 0


class DeveloperMetrics(models.Model):
    developer = models.CharField(max_length=100)
    sprint = models.CharField(max_length=100)
    points_completed = models.FloatField(default=0)
    issues_completed = models.IntegerField(default=0)
    average_time_per_point = models.FloatField(default=0)  # en horas

    class Meta:
        unique_together = ('developer', 'sprint')
        indexes = [
            models.Index(fields=['developer']),
            models.Index(fields=['sprint'])
        ]