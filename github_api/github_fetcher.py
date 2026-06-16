import os
from dotenv import load_dotenv
import requests
from time import sleep

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"token {TOKEN}"
}


def fetch_profile(username):
    """
    Fetch GitHub profile information.
    """
    url = f"https://api.github.com/users/{username}"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def fetch_github_data_for_user(username, max_retries=3):
    """
    Fetch GitHub repositories and commit information for a user.

    Returns:
    {
        "repos": [
            {
                "name": "...",
                "commits_count": ...,
                "last_commit_date": "...",
                "url": "..."
            }
        ]
    }
    """

    def get_json(url):
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url,
                    headers=HEADERS,
                    timeout=10
                )

                response.raise_for_status()

                return response.json()

            except requests.exceptions.RequestException as e:
                print(
                    f"⚠ API request failed ({attempt+1}/{max_retries}): {e}"
                )
                sleep(2)

        raise Exception(
            f"Failed to fetch {url} after {max_retries} attempts"
        )

    # Fetch all repositories
    repos_data = get_json(
        f"https://api.github.com/users/{username}/repos?per_page=100"
    )

    print(f"\nFetching GitHub data for: {username}")
    print(f"Repositories Found: {len(repos_data)}")

    result = []

    for repo in repos_data:

        repo_name = repo["name"]
        repo_url = repo["html_url"]

        try:
            commits_list = get_json(
                f"https://api.github.com/repos/{username}/{repo_name}/commits?per_page=100"
            )

            commits_count = len(commits_list)

            last_commit_date = (
                commits_list[0]["commit"]["committer"]["date"]
                if commits_list
                else "N/A"
            )

        except Exception as e:
            print(
                f"Skipping commit fetch for {repo_name}: {e}"
            )

            commits_count = 0
            last_commit_date = "N/A"

        result.append(
            {
                "name": repo_name,
                "commits_count": commits_count,
                "last_commit_date": last_commit_date,
                "url": repo_url,
            }
        )

    return {"repos": result}