import logging
import os
import re
import time
from collections import defaultdict
from time import sleep

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
logger = logging.getLogger(__name__)

HEADERS = {
    "Authorization": f"token {TOKEN}"
}

CACHE_TTL_SECONDS = int(os.getenv("GITHUB_CACHE_TTL_SECONDS", "300"))
_CACHE = {}

LANGUAGE_BUCKETS = [
    "Python",
    "Java",
    "JavaScript",
    "HTML",
    "CSS",
    "C",
    "C++",
    "Other"
]


def _cache_get(key):
    cached = _CACHE.get(key)

    if not cached:
        return None

    expires_at, value = cached

    if expires_at <= time.time():
        _CACHE.pop(key, None)
        return None

    return value


def _cache_set(key, value):
    _CACHE[key] = (
        time.time() + CACHE_TTL_SECONDS,
        value
    )


def _request_json(url, max_retries=3, skip_statuses=None, context="GitHub API request"):
    skip_statuses = set(skip_statuses or [])
    cached = _cache_get(("json", url))

    if cached is not None:
        return cached

    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=10
            )

            if response.status_code in skip_statuses:
                logger.warning(
                    "Skipping %s due to GitHub API %s: %s",
                    context,
                    response.status_code,
                    url
                )
                return None

            response.raise_for_status()
            payload = response.json()
            _cache_set(("json", url), payload)
            return payload

        except requests.exceptions.RequestException as e:
            logger.warning(
                "API request failed (%s/%s) for %s: %s",
                attempt + 1,
                max_retries,
                url,
                e
            )

            sleep(2)

    raise Exception(
        f"Failed to fetch {url} after {max_retries} attempts"
    )


def _request_response(url, max_retries=3, skip_statuses=None, context="GitHub API request"):
    skip_statuses = set(skip_statuses or [])

    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=10
            )

            if response.status_code in skip_statuses:
                logger.warning(
                    "Skipping %s due to GitHub API %s: %s",
                    context,
                    response.status_code,
                    url
                )
                return None

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            logger.warning(
                "API request failed (%s/%s) for %s: %s",
                attempt + 1,
                max_retries,
                url,
                e
            )

            sleep(2)

    raise Exception(
        f"Failed to fetch {url} after {max_retries} attempts"
    )


def fetch_profile(username):
    """
    Fetch GitHub profile information.
    """
    cache_key = ("profile", username)
    cached = _cache_get(cache_key)

    if cached is not None:
        return cached

    profile = _request_json(
        f"https://api.github.com/users/{username}",
        context=f"profile for {username}"
    )
    _cache_set(cache_key, profile)
    return profile


def _language_bucket(language):
    if language in LANGUAGE_BUCKETS and language != "Other":
        return language
    return "Other"


def _empty_language_distribution():
    return {language: 0 for language in LANGUAGE_BUCKETS}


def _build_repo_analytics(repos):
    language_distribution = _empty_language_distribution()

    for repo in repos:
        for language, amount in repo.get("languages", {}).items():
            language_distribution[_language_bucket(language)] += amount or 0

    top_language = "N/A"
    language_totals = {
        language: amount
        for language, amount in language_distribution.items()
        if amount > 0
    }

    if language_totals:
        top_language = max(
            language_totals,
            key=language_totals.get
        )

    active_repos = [
        repo for repo in repos
        if not repo.get("archived")
    ]

    most_starred_repo = "N/A"
    most_forked_repo = "N/A"

    if repos:
        most_starred_repo = max(
            repos,
            key=lambda repo: repo.get("stars", 0)
        ).get("name", "N/A")

        most_forked_repo = max(
            repos,
            key=lambda repo: repo.get("forks", 0)
        ).get("name", "N/A")

    return {
        "total_stars": sum(repo.get("stars", 0) for repo in repos),
        "total_forks": sum(repo.get("forks", 0) for repo in repos),
        "archived_repos": sum(1 for repo in repos if repo.get("archived")),
        "active_repo_count": len(active_repos),
        "most_starred_repo": most_starred_repo,
        "most_forked_repo": most_forked_repo,
        "language_distribution": language_distribution,
        "top_language": top_language
    }


def _sort_activities(activities):
    return sorted(
        activities,
        key=lambda activity: activity.get("date") if activity.get("date") != "N/A" else "",
        reverse=True
    )


def _commit_activity(repo_name, commit):
    commit_data = commit.get("commit", {})
    message = commit_data.get("message", "Commit activity")
    committer = commit_data.get("committer", {})

    return {
        "type": "Commit",
        "repo": repo_name,
        "title": message.splitlines()[0],
        "date": committer.get("date", "N/A"),
        "url": commit.get("html_url", "")
    }


def _repo_update_activity(repo):
    return {
        "type": "Repository Update",
        "repo": repo.get("name", "N/A"),
        "title": "Repository updated",
        "date": repo.get("updated_at", "N/A"),
        "url": repo.get("url", "")
    }


def _commit_count_from_link_header(link_header):
    if not link_header:
        return None

    last_link = next(
        (
            part for part in link_header.split(",")
            if 'rel="last"' in part
        ),
        ""
    )

    match = re.search(r"[?&]page=(\d+)", last_link)

    if not match:
        return None

    return int(match.group(1))


def _commit_count_from_response(response, commits):
    linked_count = _commit_count_from_link_header(
        response.headers.get("Link", "")
    )

    if linked_count is not None:
        return linked_count

    return len(commits)


def _fetch_commit_summary(username, repo_name, max_retries):
    response = _request_response(
        f"https://api.github.com/repos/{username}/{repo_name}/commits?per_page=1",
        max_retries=max_retries,
        skip_statuses={409},
        context=f"commits for {username}/{repo_name}"
    )

    if response is None:
        return 0, "N/A", []

    commits = response.json()

    if not commits:
        return 0, "N/A", []

    commits_count = _commit_count_from_response(response, commits)
    last_commit_date = commits[0].get("commit", {}).get("committer", {}).get("date", "N/A")

    latest_commits = _request_json(
        f"https://api.github.com/repos/{username}/{repo_name}/commits?per_page=5",
        max_retries=max_retries,
        skip_statuses={409},
        context=f"latest commits for {username}/{repo_name}"
    ) or commits

    return commits_count, last_commit_date, latest_commits


def sort_repos_by_last_commit(repos):
    return sorted(
        repos,
        key=lambda repo: (
            repo.get("last_commit_date") if repo.get("last_commit_date") != "N/A" else "",
            repo.get("updated_at") if repo.get("updated_at") != "N/A" else ""
        ),
        reverse=True
    )


def sort_repos_by_updated_at(repos):
    return sorted(
        repos,
        key=lambda repo: repo.get("updated_at") if repo.get("updated_at") != "N/A" else "",
        reverse=True
    )


def fetch_github_data_for_user(username, max_retries=3):
    """
    Fetch GitHub repositories, accurate commit counts, stars, forks, and language data.
    Empty or archived repositories are handled without breaking analytics.
    """
    cache_key = ("github_data", username)
    cached = _cache_get(cache_key)

    if cached is not None:
        return cached

    repos_data = _request_json(
        f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated&direction=desc",
        max_retries=max_retries,
        context=f"repositories for {username}"
    ) or []

    print(f"\nFetching GitHub data for: {username}")
    print(f"Repositories Found: {len(repos_data)}")

    result = []
    latest_commit_activities = []
    repository_update_activities = []

    for repo in repos_data:
        repo_name = repo["name"]
        repo_url = repo["html_url"]
        language = repo.get("language") or "N/A"
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        updated_at = repo.get("updated_at", "N/A")
        archived = repo.get("archived", False)
        empty = False

        try:
            commits_count, last_commit_date, latest_commits = _fetch_commit_summary(
                username,
                repo_name,
                max_retries
            )
            empty = commits_count == 0
            latest_commit_activities.extend(
                _commit_activity(repo_name, commit)
                for commit in latest_commits[:5]
            )

        except Exception as e:
            logger.warning(
                "Using zero commit data for %s/%s after commit fetch failure: %s",
                username,
                repo_name,
                e
            )
            commits_count = 0
            last_commit_date = "N/A"
            empty = True

        try:
            languages = _request_json(
                f"https://api.github.com/repos/{username}/{repo_name}/languages",
                max_retries=max_retries,
                skip_statuses={409},
                context=f"languages for {username}/{repo_name}"
            ) or {}

        except Exception as e:
            logger.warning(
                "Using empty language data for %s/%s after fetch failure: %s",
                username,
                repo_name,
                e
            )
            languages = {}

        repo_result = {
            "name": repo_name,
            "commits_count": commits_count,
            "last_commit_date": last_commit_date,
            "url": repo_url,
            "language": language,
            "stars": stars,
            "forks": forks,
            "stargazers_count": stars,
            "forks_count": forks,
            "updated_at": updated_at,
            "archived": archived,
            "empty": empty,
            "languages": languages
        }

        result.append(repo_result)
        repository_update_activities.append(
            _repo_update_activity(repo_result)
        )

    result = sort_repos_by_updated_at(result)
    analytics = _build_repo_analytics(result)
    latest_commits = _sort_activities(latest_commit_activities)[:5]
    latest_repository_updates = _sort_activities(repository_update_activities)[:5]
    analytics["latest_commits"] = latest_commits
    analytics["latest_repository_updates"] = latest_repository_updates
    analytics["recent_activities"] = _sort_activities(
        latest_commits + latest_repository_updates
    )[:5]

    data = {
        "repos": result,
        "analytics": analytics
    }
    _cache_set(cache_key, data)
    return data


def get_monthly_contributions(repos):

    monthly_data = defaultdict(int)

    for repo in repos:

        date = repo.get(
            "last_commit_date",
            ""
        )

        if date and date != "N/A":

            month = date[:7]

            monthly_data[month] += repo.get(
                "commits_count",
                0
            )

    return dict(sorted(monthly_data.items()))
