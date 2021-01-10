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

import requests
from django.dispatch import receiver
from django.db.models import signals
from .serializers import GhRepoSerializer
from .models import GithubToken, GithubRepo

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


@receiver(signals.post_save, sender=GithubToken)
def populate_gh_repos(sender, **kwargs):
    token = kwargs['instance'].token
    user = kwargs['instance'].user
    headers = {
        'Authorization': 'Token ' + token,
        'Content-Type': 'application/json'
    }
    response = requests.request(
        "POST", "https://api.github.com/graphql", headers=headers, json=gh_query)
    repos = response.json()["data"]["viewer"]["repositories"]["nodes"]

    for repo in repos:
        db_repo = GithubRepo()
        db_repo.repo_id = repo["id"]
        db_repo.user = user
        db_repo.created_at = repo["createdAt"]
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

        serializer = GhRepoSerializer(data=db_repo.__dict__)
        serializer.is_valid(raise_exception=True)
        db_repo.save()
