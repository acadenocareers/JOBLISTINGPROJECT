import os
import random
import smtplib
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO", "").split(",")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

KEYWORDS = [
    "python", "full stack", "data science", "data analyst", "power bi", "tableau",
    "flask", "digital marketing", "flutter", "frontend", "react", "html css"
]

QUOTES = [
    "Success is built one application at a time.",
    "Your future is created by what you do today.",
    "Great careers begin with brave applications.",
    "Opportunities don’t happen, you create them."
]

# ======================= FETCH JOBS =======================
def fetch_jobs():
    jobs = []

    for keyword in KEYWORDS:
        url = "https://jsearch.p.rapidapi.com/search"
        headers = {
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }

        params = {
            "query": f"{keyword} jobs in India",
            "page": "1",
            "num_pages": "1",
            "date_posted": "week"
        }

        response = requests.get(url, headers=headers, params=params, timeout=20)
        data = response.json()

        for job in data.get("data", []):
            jobs.append({
                "title": job["job_title"],
                "company": job["employer_name"],
                "link": job["job_apply_link"]
            })

    return jobs[:25]

# ======================= SEND EMAIL =======================
def send_email(jobs):
    quote = random.choice(QUOTES)
    subject = f"🎯 Job Updates — {datetime.now().strftime('%d %b %Y')}"

    html = f"<h2>{quote}</h2><hr>"

    if not jobs:
        html += "<p><b>No matching jobs found today.</b></p>"
    else:
        for job in jobs:
            html += f"""
            <div style='margin-bottom:15px'>
                <b>{job['title']}</b><br>
                {job['company']}<br>
                <a href="{job['link']}"
                   style='background:#6a00ff;color:white;padding:8px 12px;
                   border-radius:6px;text-decoration:none'>Apply Now</a>
            </div>
            """

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(EMAIL_TO)
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    print("Email sent successfully.")

# ======================= MAIN =======================
if __name__ == "__main__":
    jobs = fetch_jobs()
    send_email(jobs)
