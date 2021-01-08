from django.apps import AppConfig


class RappelConfig(AppConfig):
    name = 'rappel'

    def ready(self):
        from .github import signals
