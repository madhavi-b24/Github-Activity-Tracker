from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from students.student_manager import load_students, get_username_by_regno, generate_summary_csv
from github_api.github_fetcher import fetch_github_data_for_user
from reports.pdf_report import generate_student_pdf
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

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_repos=total_repos,
        total_commits=total_commits,
        most_active_student=most_active_student,
        leaderboard=leaderboard,
        top_students=top_students
    )

if __name__ == "__main__":
    app.run(debug=True)