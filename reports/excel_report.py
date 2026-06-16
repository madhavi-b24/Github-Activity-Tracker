# reports/excel_report.py

from openpyxl import Workbook
from pathlib import Path

REPORTS_DIR = Path("reports")


def generate_excel_report(data):

    wb = Workbook()

    ws = wb.active

    ws.title = "GitHub Summary"

    headers = [
        "RegNo",
        "Username",
        "Repositories",
        "Total Commits"
    ]

    ws.append(headers)

    for row in data:

        ws.append([
            row["regno"],
            row["username"],
            row["repos_count"],
            row["total_commits"]
        ])

    file_path = REPORTS_DIR / "summary_report.xlsx"

    wb.save(file_path)

    return file_path