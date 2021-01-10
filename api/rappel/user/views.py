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

from django.contrib.auth.signals import user_logged_out
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response

from knox.auth import TokenAuthentication
from knox.models import AuthToken

from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, UserLoginSerializer


class UserAPIView(generics.RetrieveAPIView):
    """
    Retrieve all attributes of current user
    """
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


@extend_schema(responses=UserLoginSerializer)
class RegisterAPIView(generics.CreateAPIView):
    """
    Create and log in a new user
    """
    authentication_classes = []

    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


@extend_schema(responses=UserLoginSerializer)
class LoginAPIView(generics.CreateAPIView):
    '''
    Authenticate user and return auth token
    '''
    authentication_classes = []
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class LogoutAPIView(generics.DestroyAPIView):
    '''
    Log the user out of the current session
    '''
    authentication_classes = [
        TokenAuthentication
    ]
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        self.perform_destroy(self.request._auth)
        user_logged_out.send(sender=request.user.__class__,
                             request=request, user=request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)


class LogoutAllAPIView(generics.DestroyAPIView):
    '''
    Log the user out of all sessions,
    i.e. deletes all auth tokens for the user
    '''
    authentication_classes = [
        TokenAuthentication
    ]
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        request.user.auth_token_set.all().delete()
        user_logged_out.send(sender=request.user.__class__,
                             request=request, user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
