def print_repo_data(repo_data):
    for repo in repo_data:
        print(f"Repo: {repo['repo_name']}")
        print(f"  Total Commits: {repo['total_commits']}")
        print(f"  Last Commit: {repo['last_commit']}")
        print("-" * 30)