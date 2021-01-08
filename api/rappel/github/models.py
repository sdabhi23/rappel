from datetime import datetime, timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class GithubToken(models.Model):
    token = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now=True)


class GithubRepo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    repo_id = models.CharField(max_length=50, primary_key=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    pushed_at = models.DateTimeField()
    is_archived = models.BooleanField()
    is_empty = models.BooleanField()
    is_fork = models.BooleanField()
    is_private = models.BooleanField()
    is_owner = models.BooleanField()
    license = models.CharField(max_length=20, null=True)
    name = models.CharField(max_length=110)
    owner = models.CharField(max_length=39)
    description = models.TextField(blank=True, default="")
    language_1 = models.JSONField(null=True)
    language_2 = models.JSONField(null=True)
    language_3 = models.JSONField(null=True)
    pr_count = models.IntegerField()
    star_count = models.IntegerField()
    fork_count = models.IntegerField()
    watcher_count = models.IntegerField()
    release_count = models.IntegerField()
    vulnerability_count = models.IntegerField()
    url = models.URLField()
    hidden = models.BooleanField(default=False)
    rappel_created_at = models.DateTimeField(auto_now_add=True)
    rappel_updated_at = models.DateTimeField(auto_now=True)

    class StatusOfRepo(models.IntegerChoices):
        BACKLOG = 0, _('Backlog')
        ACTIVE = 1, _('Active')
        WIP = 2, _('Work In Progess')
        DONE = 3, _('Done')
        ARCHIVE = 4, _('Archive')

    status = models.IntegerField(
        choices=StatusOfRepo.choices,
        default=StatusOfRepo.BACKLOG,
    )

    notes = models.TextField(blank=True, default="")

    @property
    def age(self):
        delta = datetime.now(timezone.utc) - self.created_at
        return round(delta.days / 365, 2)

    class Meta:
        ordering = ["-rappel_updated_at"]
