from django.utils.translation import gettext_lazy as _
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class KnoxTokenAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'knox.auth.TokenAuthentication'  # full import path OR class ref
    name = 'Knox Token Authentication'  # name used in the schema

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': _('Token-based authentication with required prefix "Token"')
        }
