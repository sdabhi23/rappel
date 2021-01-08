from django.db import models
from rest_framework import serializers

from .models import GithubToken, GithubRepo


class GhTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = GithubToken
        fields = ('id', 'token', 'created_on')


class AddGhTokenSerializer(serializers.Serializer):
    code = serializers.CharField()
    state = serializers.CharField()


class GhRepoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GithubRepo
        exclude = ['user']
    age = serializers.ReadOnlyField()
