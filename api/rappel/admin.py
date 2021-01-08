from django.contrib import admin
from .github.models import GithubRepo, GithubToken

admin.site.register(GithubToken)
admin.site.register(GithubRepo)