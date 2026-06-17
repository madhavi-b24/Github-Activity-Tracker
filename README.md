# 🚀 GitHub Student Analytics Platform

A Flask-based dashboard for tracking student GitHub activity, repository progress, contribution trends, leaderboard rankings, and downloadable reports.

---

## 📌 Overview

GitHub Student Analytics Platform helps faculty, mentors, and students monitor GitHub performance through interactive analytics, contribution tracking, repository insights, and automated reports.

The platform integrates with the GitHub API to collect repository and commit information and presents it through a clean analytics dashboard.

---

## ✨ Features

### 👨‍🎓 Student Analytics

- Student analytics by registration number
- GitHub profile insights
- Total repositories
- Total commits
- Most active repository
- Recently active repositories
- Monthly contribution chart
- Programming language distribution chart
- Stars and forks analytics
- GitHub profile link

### 🏆 Student Leaderboard

- Rank students based on total commits
- View top contributors
- Compare GitHub activity among students

### 📂 Student Directory

- Browse all registered students
- Search by Registration Number
- Search by GitHub Username
- Quick access to analytics pages

### 📊 Repository Analytics

- Repository details page
- Commit count tracking
- Last commit date
- Repository activity analysis
- Repository links

### 📈 Data Visualization

- Repository Commit Analysis Chart
- Monthly Contribution Activity Chart
- Programming Language Distribution Pie Chart
- Contribution Trends

### 📄 Report Generation

- Individual Student PDF Reports
- CSV Summary Export
- Excel Report Export

### ⚡ Additional Features

- Recent activity tracking
- Graceful handling of GitHub API errors
- Search functionality
- Responsive dashboard design

---

## 🛠️ Tech Stack

### Backend

- Python
- Flask
- Requests
- Pandas
- OpenPyXL
- FPDF

### Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript

### Visualization

- Chart.js

### API

- GitHub REST API

---

## 📂 Project Structure

```text
github_activity_tracker/
│
├── app.py
├── github_fetcher.py
├── student_data.py
├── users.csv
│
├── templates/
│   ├── home.html
│   ├── student_analytics.html
│   ├── students.html
│   ├── leaderboard.html
│   ├── repository_details.html
│
├── reports/
├── static/
├── .env
├── requirements.txt
└── README.md
```

---

## 🔑 Environment Variables

Create a `.env` file:

```env
GITHUB_TOKEN=your_github_personal_access_token
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/madhavi-b24/GitHub-Activity-Tracker.git
cd GitHub-Activity-Tracker
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Linux / Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run Application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## 📸 Screenshots

### Home Dashboard
Add Screenshot Here

### Student Analytics
Add Screenshot Here

### Student Directory
Add Screenshot Here

### Leaderboard
Add Screenshot Here

### Repository Details
Add Screenshot Here

---

## 📊 Analytics Provided

The platform tracks:

- Total Repositories
- Total Commits
- Monthly Contributions
- Active Repositories
- Repository Commit Counts
- Programming Languages Used
- Stars and Forks
- GitHub Profile Insights
- Student Rankings

---

## 🎯 Use Cases

- Student Progress Tracking
- Faculty Evaluation
- GitHub Portfolio Analysis
- Open Source Contribution Monitoring
- Academic Project Assessment
- Coding Activity Monitoring

---

## 🚀 Future Improvements

- Contribution Heatmaps
- Student Comparison Dashboard
- Advanced Filtering
- Deployment Support
- Team Analytics
- Organization Analytics

---

## 👩‍💻 Author

### Bonda Papa Madhavi

B.Tech Information Technology

GitHub: https://github.com/madhavi-b24

---

## 🙏 Acknowledgements

- GitHub REST API
- Flask
- Bootstrap
- Chart.js
- Open Source Community

---

⭐ If you found this project useful, please consider giving it a star.