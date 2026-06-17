from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from students.student_manager import load_students, get_username_by_regno, generate_summary_csv
from github_api.github_fetcher import (
    fetch_github_data_for_user,
    fetch_profile,
    get_monthly_contributions,
    sort_repos_by_last_commit,
    sort_repos_by_updated_at
)
from reports.pdf_report import generate_student_pdf
from reports.excel_report import generate_excel_report
from pathlib import Path
import logging

app = Flask(__name__)
app.secret_key = "supersecretkey"
REPORTS_DIR = Path("reports")
logger = logging.getLogger(__name__)

def _sum_repo_values(repos, key):
    return sum(repo.get(key, 0) for repo in repos)


def _active_repositories(repos):
    return [
        repo for repo in repos
        if not repo.get("archived")
        and not repo.get("empty")
        and repo.get("last_commit_date") != "N/A"
    ]


def _top_repositories_by_commits(repos, limit=5):
    return sorted(
        repos,
        key=lambda repo: repo.get("commits_count", 0),
        reverse=True
    )[:limit]


def _find_student_matches(query, students):
    normalized_query = (query or "").strip().lower()

    if not normalized_query:
        return []

    exact_matches = [
        (regno, username)
        for regno, username in students.items()
        if regno.lower() == normalized_query
        or username.lower() == normalized_query
    ]

    if exact_matches:
        return exact_matches

    return [
        (regno, username)
        for regno, username in students.items()
        if normalized_query in regno.lower()
        or normalized_query in username.lower()
    ]


def _student_repo_summary(regno, username):
    data = fetch_github_data_for_user(username)
    repos = data.get("repos", [])
    total_commits = _sum_repo_values(repos, "commits_count")

    return {
        "regno": regno,
        "username": username,
        "repos": repos,
        "repos_count": len(repos),
        "total_commits": total_commits,
        "analytics": data.get("analytics", {})
    }


def _platform_statistics(students):
    stats = {
        "total_students": len(students),
        "total_repos": 0,
        "total_commits": 0,
        "total_stars": 0
    }

    for username in students.values():
        try:
            data = fetch_github_data_for_user(username)
            repos = data.get("repos", [])
            analytics = data.get("analytics", {})

            stats["total_repos"] += len(repos)
            stats["total_commits"] += _sum_repo_values(repos, "commits_count")
            stats["total_stars"] += analytics.get(
                "total_stars",
                _sum_repo_values(repos, "stars")
            )

        except Exception as e:
            logger.warning(
                "Error fetching platform statistics for %s: %s",
                username,
                e
            )

    return stats


@app.route("/")
def home():
    students = load_students()
    stats = _platform_statistics(students)

    return render_template(
        "home.html",
        **stats
    )

@app.route("/summary", methods=["POST"])
def summary():
    students = load_students()
    all_data = []

    count = request.form.get("count")
    try:
        count = int(count)
    except (ValueError, TypeError):
        count = len(students)

    selected_students = dict(list(students.items())[:count])

    for regno, username in selected_students.items():
        try:
            summary = _student_repo_summary(regno, username)
            all_data.append({
                "regno": regno,
                "username": username,
                "repos_count": summary["repos_count"],
                "total_commits": summary["total_commits"]
            })
        except Exception as e:
            print(f"⚠️ Error fetching {username}: {e}")

    if not all_data:
        flash("No data available to generate summary CSV.", "danger")
        return redirect(url_for("home"))

    generate_summary_csv(all_data)
    return send_file(str(REPORTS_DIR / "summary_report.csv"), as_attachment=True)

@app.route("/student_pdf", methods=["POST"])
def student_pdf():
    regno = request.form.get("regno")
    username = get_username_by_regno(regno)
    if not username:
        flash(f"No student found with RegNo {regno}", "danger")
        return redirect(url_for("home"))

    try:
        data = fetch_github_data_for_user(username)
        repos = data.get("repos", [])
        generate_student_pdf(username, repos)
        return send_file(str(Path("reports") / f"{username}_report.pdf"), as_attachment=True)
    except Exception as e:
        flash(f"Error generating PDF: {e}", "danger")
        return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    students = load_students()

    total_students = len(students)
    total_repos = 0
    total_commits = 0

    most_active_student = "N/A"
    max_commits = 0

    leaderboard = []

    for regno, username in students.items():
        try:
            summary = _student_repo_summary(regno, username)
            commits = summary["total_commits"]

            total_repos += summary["repos_count"]
            total_commits += commits

            leaderboard.append({
                "username": username,
                "commits": commits
            })

            if commits > max_commits:
                max_commits = commits
                most_active_student = username

        except Exception as e:
            logger.warning("Error fetching dashboard data for %s: %s", username, e)

    leaderboard = sorted(
        leaderboard,
        key=lambda x: x["commits"],
        reverse=True
    )

    top_students = leaderboard[:5]
    student_names = [
    student["username"]
    for student in leaderboard
     ]

    student_commits = [
    student["commits"]
    for student in leaderboard
    ]

    return render_template(
        "dashboard.html",
        student_names=student_names,
        student_commits=student_commits,
        total_students=total_students,
        total_repos=total_repos,
        total_commits=total_commits,
        most_active_student=most_active_student,
        leaderboard=leaderboard,
        top_students=top_students
    )
@app.route("/student/<regno>")
def student_analytics(regno):

    username = get_username_by_regno(regno)

    if not username:
        flash("Student not found", "danger")
        return redirect(url_for("home"))

    try:

        data = fetch_github_data_for_user(username)

        profile = fetch_profile(username)

        repos = data.get("repos", [])
        monthly_contributions = dict(sorted(
            get_monthly_contributions(repos).items()
        ))
        print(monthly_contributions)

        months = list(
    monthly_contributions.keys()
     )

        month_commits = list(
    monthly_contributions.values()
    )

        total_repos = len(repos)

        total_commits = _sum_repo_values(repos, "commits_count")

        repo_analytics = data.get("analytics", {})
        language_distribution = repo_analytics.get(
            "language_distribution",
            {}
        )
        top_language = repo_analytics.get("top_language", "N/A")

        active_candidates = _active_repositories(repos)
        most_active_repo = "N/A"

        if active_candidates:
            most_active_repo = max(
                active_candidates,
                key=lambda r: r.get("commits_count", 0)
            )["name"]

        active_repos = sort_repos_by_last_commit(active_candidates)[:5]
        recent_repos = sort_repos_by_updated_at(repos)[:5]
        top_repositories = _top_repositories_by_commits(repos)

        return render_template(
            "student_analytics.html",
            regno=regno,
            username=username,
            total_repos=total_repos,
            total_commits=total_commits,
            total_stars=repo_analytics.get(
                "total_stars",
                _sum_repo_values(repos, "stars")
            ),
            total_forks=repo_analytics.get(
                "total_forks",
                _sum_repo_values(repos, "forks")
            ),
            archived_repos=repo_analytics.get("archived_repos", 0),
            active_repo_count=repo_analytics.get(
                "active_repo_count",
                len(active_candidates)
            ),
            most_starred_repo=repo_analytics.get("most_starred_repo", "N/A"),
            most_forked_repo=repo_analytics.get("most_forked_repo", "N/A"),
            most_active_repo=most_active_repo,
            top_language=top_language,
            active_repos=active_repos,
            recent_repos=recent_repos,
            top_repositories=top_repositories,
            latest_commits=repo_analytics.get("latest_commits", []),
            latest_repository_updates=repo_analytics.get(
                "latest_repository_updates",
                []
            ),
            recent_activities=repo_analytics.get("recent_activities", []),
            profile=profile,
            months=months,
            month_commits=month_commits,
            language_labels=list(language_distribution.keys()),
            language_values=list(language_distribution.values()),
            repos=repos
        )

    except Exception as e:

        flash(str(e), "danger")
 
        return redirect(url_for("home"))
    
@app.route("/students")
def students():

    students_data = load_students()

    return render_template(
        "students.html",
        students=students_data
    )
@app.route("/repository/<username>/<repo_name>")
def repository_details(username, repo_name):

    try:
        data = fetch_github_data_for_user(username)
        repos = data.get("repos", [])
    except Exception as e:
        logger.warning(
            "Error fetching repository details for %s/%s: %s",
            username,
            repo_name,
            e
        )
        flash("Unable to load repository details right now.")
        return redirect(url_for("home"))

    selected_repo = None

    for repo in repos:

        if repo["name"] == repo_name:

            selected_repo = repo

            break

    if not selected_repo:

        flash("Repository not found")

        return redirect(url_for("home"))

    return render_template(
        "repository_details.html",
        repo=selected_repo,
        username=username
    )


@app.route("/leaderboard")
def leaderboard():

    students = load_students()

    rankings = []

    for regno, username in students.items():

        try:

            summary = _student_repo_summary(regno, username)
            commits = summary["total_commits"]

            rankings.append({
                "regno": regno,
                "username": username,
                "commits": commits
            })

        except Exception as e:

            logger.warning("Error fetching leaderboard data for %s: %s", username, e)

    rankings = sorted(
        rankings,
        key=lambda x: x["commits"],
        reverse=True
    )

    return render_template(
        "leaderboard.html",
        rankings=rankings
    )

@app.route("/excel", methods=["POST"])
def excel_report():

    students = load_students()

    all_data = []

    for regno, username in students.items():

        try:

            summary = _student_repo_summary(regno, username)

            all_data.append({
                "regno": regno,
                "username": username,
                "repos_count": summary["repos_count"],
                "total_commits": summary["total_commits"]
            })

        except Exception as e:
            logger.warning("Error fetching Excel data for %s: %s", username, e)

    file_path = generate_excel_report(all_data)

    return send_file(
        file_path,
        as_attachment=True
    )
@app.route("/search_student", methods=["POST"])
def search_student():

    query = request.form.get("regno")
    students = load_students()
    matches = _find_student_matches(query, students)

    if len(matches) == 1:
        regno, username = matches[0]
        return redirect(
            url_for(
                "student_analytics",
                regno=regno
            )
        )

    if len(matches) > 1:
        flash(
            f"Multiple students matched '{query}'. Please refine your search.",
            "warning"
        )
        return redirect(url_for("students"))

    flash(
        f"No student found matching '{query}'",
        "danger"
    )

    return redirect(
        url_for("home")
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)
