# 📊 GitHub Tracker (PDF & Bulk Excel)

![Python](https://img.shields.io/badge/Python-3.10-blue)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Output](https://img.shields.io/badge/Output-PDF%2FExcel-green)

**GitHub Tracker** is a Python tool that helps track GitHub statistics for **repositories** or **students**. It supports:

* Generating **PDF reports** for repository activity metrics.
* Generating **Excel reports** for multiple student GitHub profiles with ranking.

This makes it ideal for **developers, educators, and mentors** who want **automated insights** into GitHub contributions.

---

## 🚀 Features

### PDF Tracker (Repositories)

* Fetch repository data using the **GitHub API**.
* Generate **PDF reports** for:

  * Issues (open/closed, assigned, labels)
  * Pull Requests (status, merge info)
  * Commit activity
* Command-line interface for quick use.
* Requires a **GitHub API token**.

### Excel Tracker (Bulk Students)

* Read multiple student records from an **Excel sheet**.
* Fetch GitHub profile data and repository stats.
* Generate a **detailed Excel report** with columns:

  * Rank
  * Student Name
  * College Email
  * GitHub Username
  * Followers
  * Public Repositories
  * Total Stars
  * Total Forks
  * Last Activity Date
  * Status (Success / Invalid Username)
* Automatically **rank students** based on total stars.
* Handles missing or invalid usernames gracefully.
* Minimal setup; only requires **Python 3.10+**, `requests`, `openpyxl`.

---
## 🛠 Installation

1. Clone the repository:

```bash
git clone https://github.com/Sathvika-g-29/Github_Tracker.git
cd Github_Tracker
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

> Ensure **Python 3.10+** is installed.

---

## 🔑 Setup

### PDF Tracker

1. Generate a **GitHub personal access token**: [GitHub Developer Settings](https://github.com/settings/tokens)
2. Keep the token ready; you’ll need it when running the PDF tracker script.

### Excel Tracker

1. Create an **input Excel file** named `students_input.xlsx` with headers:

| Student Name | College Email | GitHub Username |
| ------------ | ------------- | --------------- |

2. Fill student data **starting from row 2**.
3. Ensure the Excel file is **saved and closed** before running the script.
4. Optionally, set your GitHub token as an environment variable `GITHUB_TOKEN` for higher API limits.

---

## ▶ How to Use

### PDF Tracker

Run the script for repository reports:

```bash
python main.py
```

* Enter the **repository name** (e.g., `username/repo`) when prompted.
* Enter your **GitHub token**.
* A **PDF report** will be generated in the project directory.

### Excel Tracker (Bulk Students)

Run the script for student GitHub reports:

```bash
python student_tracker.py
```

* The script will:

  1. Read all student GitHub usernames from the Excel file
  2. Fetch profile and repository data from GitHub
  3. Rank students by total stars
  4. Generate `students_report.xlsx` with all metrics

> ⚠️ Ensure the input Excel file is **closed** before running to avoid `PermissionError`.

---

## 🧪 Testing with Bulk Data

You can add **fake student entries** to test the Excel tracker:

| Student Name   | College Email                                 | GitHub Username |
| -------------- | --------------------------------------------- | --------------- |
| Test Student 1 | [test1@college.edu](mailto:test1@college.edu) | octocat         |
| Test Student 2 | [test2@college.edu](mailto:test2@college.edu) | torvalds        |

> Replace with real GitHub usernames for actual reports.

---

## 👥 Contribution Guidelines

Contributions are welcome! You can help by:

* Reporting bugs or issues
* Suggesting new features
* Adding support for more GitHub metrics
* Improving code readability or performance

**Workflow:** Fork → Create feature branch → Make changes → Open Pull Request

---
