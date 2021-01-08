import os
import json
import requests
from knox.auth import TokenAuthentication
from django.db.utils import IntegrityError
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, generics, status

from .serializers import AddGhTokenSerializer, GhRepoSerializer, GhTokenSerializer
from .models import GithubRepo, GithubToken

gh_query = {
    "query": '''
{
  viewer {
    repositories(first: 100, orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes {
        description
        forkCount
        createdAt
        id
        isArchived
        isEmpty
        isFork
        isPrivate
        licenseInfo {
          spdxId
        }
        name
        owner {
          login
        }
        languages(first: 3, orderBy: {field: SIZE, direction: DESC}) {
          nodes {
            name
            color
          }
        }
        pullRequests {
          totalCount
        }
        pushedAt
        releases {
          totalCount
        }
        stargazerCount
        updatedAt
        url
        viewerPermission
        vulnerabilityAlerts {
          totalCount
        }
        watchers {
          totalCount
        }
      }
    }
  }
}
    ''',
    "variables": {}
}


class ListGithubTokens(generics.ListAPIView):
    """
    List all GitHub tokens for the current user
    """
    authentication_classes = [
        TokenAuthentication
    ]
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = GhTokenSerializer

    def get_queryset(self):
        return GithubToken.objects.filter(user=self.request.user)


@extend_schema(request=AddGhTokenSerializer)
class AddGithubToken(generics.CreateAPIView):
    """
    Add new GitHub token for the current user
    """
    authentication_classes = [
        TokenAuthentication
    ]
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def post(self, request, *args, **kwargs):
        body = json.loads(request.body)
        gh_res = requests.post("https://github.com/login/oauth/access_token",
                               headers={
                                   "Accept": "application/json"
                               },
                               data={
                                   "client_id": os.environ['GITHUB_CLIENT_ID'],
                                   "client_secret": os.environ['GITHUB_CLIENT_SECRET'],
                                   "code": body['code'],
                                   "state": body['state']
                               })
        gh_data = gh_res.json()
        github_token = GithubToken(
            user=request.user, token=gh_data["access_token"])
        github_token.save()
        return Response(status=status.HTTP_200_OK)


class ListGithubRepos(generics.ListAPIView):
    """
    List all visible GitHub repos for the current user
    """
    authentication_classes = [
        TokenAuthentication
    ]
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = GhRepoSerializer

    def get_queryset(self):
        return GithubRepo.objects.filter(user=self.request.user, hidden=False)


class GetGithubRepo(generics.RetrieveAPIView):
    """
    Get details of a GitHub repo of the current user
    """
    authentication_classes = [
        TokenAuthentication
    ]
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = GhRepoSerializer

    def get(self, request, *args, **kwargs):
        return Response(GhRepoSerializer(GithubRepo.objects.get(pk=kwargs['repo_id'])).data, status=status.HTTP_200_OK)


@extend_schema(request=GhRepoSerializer)
class UpdateGithubRepo(generics.UpdateAPIView):
    """
    Update metadata of a GitHub repo of the current user
    """
    authentication_classes = [
        TokenAuthentication
    ]
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def patch(self, request, *args, **kwargs):
        repo = generics.get_object_or_404(GithubRepo, pk=kwargs['repo_id'])
        serializer = GhRepoSerializer(repo, data=request.data, partial=True)
        if serializer.is_valid():
            repo = serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(responses={"200": GhRepoSerializer})
class FetchGithubRepos(generics.GenericAPIView):
    """
    Fetch and update metadata of all repos from GitHub
    """
    authentication_classes = [
        TokenAuthentication
    ]
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = GhRepoSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        token = GithubToken.objects.filter(user=user)[0].token
        headers = {
            'Authorization': 'Token ' + token,
            'Content-Type': 'application/json'
        }

        response = requests.request(
            "POST", "https://api.github.com/graphql", headers=headers, json=gh_query)
        repos = response.json()["data"]["viewer"]["repositories"]["nodes"]

        for repo in repos:
            try:
                db_repo = GithubRepo.objects.get(pk=repo["id"])
                new_obj = False
            except GithubRepo.DoesNotExist:
                db_repo = GithubRepo()
                db_repo.repo_id = repo["id"]
                db_repo.user = user
                db_repo.created_at = repo["createdAt"]
                new_obj = True

            db_repo.updated_at = repo["updatedAt"]
            db_repo.pushed_at = repo["pushedAt"]
            db_repo.is_archived = repo["isArchived"]
            db_repo.is_empty = repo["isEmpty"]
            db_repo.is_fork = repo["isFork"]
            db_repo.is_private = repo["isPrivate"]
            db_repo.is_owner = (repo["viewerPermission"] == "ADMIN")
            try:
                db_repo.license = repo["licenseInfo"]["spdxId"]
            except TypeError:
                db_repo.license = None
            db_repo.name = repo["name"]
            db_repo.owner = repo["owner"]["login"]
            if repo["description"] != None:
                db_repo.description = repo["description"]
            try:
                db_repo.language_1 = repo["languages"]["nodes"][0]
            except IndexError:
                db_repo.language_1 = None
            try:
                db_repo.language_2 = repo["languages"]["nodes"][1]
            except IndexError:
                db_repo.language_2 = None
            try:
                db_repo.language_3 = repo["languages"]["nodes"][2]
            except IndexError:
                db_repo.language_3 = None
            db_repo.pr_count = repo["pullRequests"]["totalCount"]
            db_repo.star_count = repo["stargazerCount"]
            db_repo.fork_count = repo["forkCount"]
            db_repo.watcher_count = repo["watchers"]["totalCount"]
            db_repo.release_count = repo["releases"]["totalCount"]
            db_repo.vulnerability_count = repo["vulnerabilityAlerts"]["totalCount"]
            db_repo.url = repo["url"]

            if db_repo.is_archived:
                db_repo.status = db_repo.StatusOfRepo.ARCHIVE

            if new_obj:
                serializer = GhRepoSerializer(data=db_repo.__dict__)
                serializer.is_valid(raise_exception=True)
                db_repo.save()
            else:
                db_repo.save(force_update=True)

        return Response(GhRepoSerializer(GithubRepo.objects.filter(user=user, hidden=False), many=True).data, status=status.HTTP_200_OK)
