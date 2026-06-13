from fpdf import FPDF
from pathlib import Path

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

def generate_student_pdf(username, repos):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"GitHub Report - {username}", ln=True, align="C")
    pdf.ln(5)

    # Table headers
    headers = ["Project Name", "Commits", "Last Commit Date", "URL"]
    col_widths = [80, 30, 50, 120]

    pdf.set_font("Arial", 'B', 12)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align='C')
    pdf.ln()

    pdf.set_font("Arial", '', 11)
    for repo in repos:
        # Project Name
        pdf.multi_cell(col_widths[0], 8, str(repo.get("name", "")), border=1)
        x = pdf.get_x()
        y = pdf.get_y() - 8
        pdf.set_xy(x + col_widths[0], y)
        # Commits
        pdf.cell(col_widths[1], 8, str(repo.get("commits_count", 0)), border=1)
        # Last Commit Date
        pdf.cell(col_widths[2], 8, str(repo.get("last_commit_date", "")), border=1)
        # URL as clickable hyperlink
        pdf.set_font("Arial", 'U', 11)  # underline to indicate link
        pdf.cell(col_widths[3], 8, repo.get("url", ""), border=1, ln=1, link=repo.get("url", ""))
        pdf.set_font("Arial", '', 11)  # reset font for next row

    file_path = REPORTS_DIR / f"{username}_report.pdf"
    pdf.output(file_path)
    print(f"✅ PDF saved: {file_path}")