from pathlib import Path
from students.student_manager import load_students, generate_summary_csv
from github_api.github_fetcher import fetch_github_data_for_user
from reports.pdf_generator import generate_pdf

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def process_all_students(generate_summary=True):
    students = load_students()
    if not students:
        print("No students found in students.csv")
        return
    
    summary_data = []

    for regno, username in students.items():
        print(f"Processing {regno} -> {username} ...")
        data = fetch_github_data_for_user(username)
        
        if data.get("error"):
            print(f"  ❌ Error for {username}: {data['error']}")
            continue
        
        # Add data for summary CSV
        summary_data.append({
            "regno": regno,
            "username": username,
            "repos_count": len(data["repos"]),
            "total_commits": sum([repo.get("commits_count", 0) for repo in data["repos"]])
        })
        
        # Generate detailed PDF for each student
        pdf_filename = REPORTS_DIR / f"{regno}_{username}_report.pdf"
        generate_pdf(username, data["repos"])
        print(f"  ✅ PDF saved: {pdf_filename}")

    # Generate summary CSV if requested
    if generate_summary:
        generate_summary_csv(summary_data)

if __name__ == "__main__":
    process_all_students()