import os
import requests
from time import sleep

TOKEN = os.getenv("GITHUB_TOKEN")
#if not TOKEN:
 #   raise Exception("⚠️ Please set the environment variable GITHUB_TOKEN before running.")

HEADERS = {"Authorization": f"token {TOKEN}"}

def fetch_github_data_for_user(username, max_retries=3):
    """
    Fetch GitHub repositories and commit info for a user.
    Returns: { "repos": [ { "name": ..., "commits_count": ..., "last_commit_date": ..., "url": ... } ] }
    """
    def get_json(url):
        for attempt in range(max_retries):
            try:
                resp = requests.get(url, headers=HEADERS, timeout=10)
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.RequestException as e:
                print(f"⚠️ API request failed ({attempt+1}/{max_retries}): {e}")
                sleep(2)
        raise Exception(f"Failed to fetch {url} after {max_retries} attempts")

    repos_data = get_json(f"https://api.github.com/users/{username}/repos?per_page=100")
    result = []
    for repo in repos_data:
        repo_name = repo["name"]
        repo_url = repo["html_url"]
        commits_list = get_json(f"https://api.github.com/repos/{username}/{repo_name}/commits?per_page=100")
        result.append({
            "name": repo_name,
            "commits_count": len(commits_list),
            "last_commit_date": commits_list[0]["commit"]["committer"]["date"] if commits_list else "N/A",
            "url": repo_url
        })
    return {"repos": result}