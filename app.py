from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from students.student_manager import load_students, get_username_by_regno, generate_summary_csv
from github_api.github_fetcher import (
    fetch_github_data_for_user,
    fetch_profile,
    get_monthly_contributions
)
from reports.pdf_report import generate_student_pdf
from reports.excel_report import generate_excel_report
from pathlib import Path

app = Flask(__name__)
app.secret_key = "supersecretkey"
REPORTS_DIR = Path("reports")

@app.route("/")
def home():
    return render_template("home.html")

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
            data = fetch_github_data_for_user(username)
            profile=fetch_profile(username)
            repos = data.get("repos", [])
            total_commits = sum(r.get("commits_count", 0) for r in repos)
            all_data.append({
                "regno": regno,
                "username": username,
                "repos_count": len(repos),
                "total_commits": total_commits
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
            data = fetch_github_data_for_user(username)
            repos = data.get("repos", [])

            commits = sum(
                repo.get("commits_count", 0)
                for repo in repos
            )

            total_repos += len(repos)
            total_commits += commits

            leaderboard.append({
                "username": username,
                "commits": commits
            })

            if commits > max_commits:
                max_commits = commits
                most_active_student = username

        except Exception as e:
            print(f"Error fetching data for {username}: {e}")

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
        monthly_contributions = get_monthly_contributions(
    repos
    )
        print(monthly_contributions)

        months = list(
    monthly_contributions.keys()
     )

        month_commits = list(
    monthly_contributions.values()
    )

        total_repos = len(repos)

        total_commits = sum(
            repo.get("commits_count", 0)
            for repo in repos
        )

        most_active_repo = "N/A"

        if repos:
            most_active_repo = max(
                repos,
                key=lambda r: r.get("commits_count", 0)
            )["name"]

        recent_repos = sorted( repos,
          key=lambda x: x.get("updated_at", ""),
    reverse=True)[:5]

        return render_template(
            "student_analytics.html",
            regno=regno,
            username=username,
            total_repos=total_repos,
            total_commits=total_commits,
            most_active_repo=most_active_repo,
            recent_repos=recent_repos,
            profile=profile,
            months=months,
            month_commits=month_commits,
            repos=repos
        )

    except Exception as e:

        flash(str(e), "danger")
        return redirect(url_for("home"))

@app.route("/excel", methods=["POST"])
def excel_report():

    students = load_students()

    all_data = []

    for regno, username in students.items():

        try:

            data = fetch_github_data_for_user(username)

            repos = data.get("repos", [])

            total_commits = sum(
                repo.get("commits_count", 0)
                for repo in repos
            )

            all_data.append({
                "regno": regno,
                "username": username,
                "repos_count": len(repos),
                "total_commits": total_commits
            })

        except Exception as e:
            print(e)

    file_path = generate_excel_report(all_data)

    return send_file(
        file_path,
        as_attachment=True
    )
@app.route("/search_student", methods=["POST"])
def search_student():

    regno = request.form.get("regno")

    return redirect(
        url_for(
            "student_analytics",
            regno=regno
        )
    )

if __name__ == "__main__":
    app.run(debug=True)