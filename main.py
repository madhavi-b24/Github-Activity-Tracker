from flask import Flask, render_template, request, send_file
from students.student_manager import load_students, get_username_by_regno, generate_summary_csv
from github_api.github_fetcher import fetch_github_data_for_user
from reports.pdf_report import generate_student_pdf
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "summary":
            all_students = load_students()
            all_data = []
            for regno, username in all_students.items():
                try:
                    data = fetch_github_data_for_user(username)
                    total_commits = sum(repo.get("commits_count", 0) for repo in data.get("repos", []))
                    all_data.append({
                        "regno": regno,
                        "username": username,
                        "repos_count": len(data.get("repos", [])),
                        "total_commits": total_commits
                    })
                except:
                    continue
            generate_summary_csv(all_data)
            message = "✅ Summary CSV generated at reports/summary_report.csv"
        
        elif action == "pdf":
            regno = request.form.get("regno").strip()
            username = get_username_by_regno(regno)
            if not username:
                message = f"❌ No student found with RegNo {regno}"
            else:
                try:
                    data = fetch_github_data_for_user(username)
                    generate_student_pdf(username, data.get("repos", []))
                    message = f"✅ PDF generated at reports/{username}_report.pdf"
                except Exception as e:
                    message = f"❌ Error generating PDF: {e}"
                    
    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)