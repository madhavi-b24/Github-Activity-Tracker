from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from pathlib import Path

def generate_pdf(username, repos):
    """
    Generate PDF report for a student.
    repos: list of dicts: { "name": ..., "url": ..., "commits_count": ... }
    """
    REPORTS_DIR = Path("reports")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    filename = REPORTS_DIR / f"{username}_report.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    title = Paragraph(f"<b>GitHub Report for {username}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Table data
    data = [["Project Name", "URL", "Commits"]]
    for repo in repos:
        name = repo.get("name", "")
        url = repo.get("url", "")
        commits = repo.get("commits_count", 0)
        data.append([name, url, commits])

    table = Table(data, colWidths=[150, 250, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black)
    ]))
    elements.append(table)

    doc.build(elements)
    print(f"✅ PDF saved: {filename}")