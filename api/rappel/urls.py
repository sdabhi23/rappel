# Copyright 2021 Shrey Dabhi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView
from drf_spectacular import renderers
from django.contrib import admin
from django.urls import path

from .user.views import UserAPIView, RegisterAPIView, LoginAPIView, LogoutAPIView, LogoutAllAPIView
from .github.views import FetchGithubRepos, GetGithubRepo, ListGithubRepos, ListGithubTokens, AddGithubToken, UpdateGithubRepo
from .extensions import *


urlpatterns = [

    # Schema
    path('api/schema/', SpectacularAPIView().as_view(
        renderer_classes=[renderers.OpenApiJsonRenderer2]), name='schema'),
    path('api/schema/redoc/',
         SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Auth APIs
    path('api/auth/user/', UserAPIView.as_view(), name='user'),
    path('api/auth/register/', RegisterAPIView.as_view(), name='register'),
    path('api/auth/login/', LoginAPIView.as_view(), name='login'),
    path('api/auth/logout/', LogoutAPIView.as_view(), name='logout'),
    path('api/auth/logoutall/', LogoutAllAPIView.as_view(), name='logout-all'),

    # Github related APIs
    path('api/github/tokens/', AddGithubToken.as_view(), name='add-gh-token'),
    path('api/github/tokens/', ListGithubTokens.as_view(), name='list-gh-tokens'),
    path('api/github/repos/', ListGithubRepos.as_view(), name='list-gh-repos'),
    path('api/github/repos/<str:repo_id>/',
         GetGithubRepo.as_view(), name='get-gh-repo'),
    path('api/github/repos/update/<str:repo_id>/',
         UpdateGithubRepo.as_view(), name='update-gh-repo'),
    path('api/github/refresh/', FetchGithubRepos.as_view(), name='fetch-gh-repos'),

    # Django Admin
    path('admin/', admin.site.urls),
]
