import os
import requests
import smtplib
import random
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# ========== CONFIG ==========
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO").split(",")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

QUOTES = [
    "Success is built one application at a time.",
    "Your future is created by what you do today.",
    "Great careers begin with brave applications.",
    "Opportunities don’t happen, you create them.",
    "Small steps today lead to big success tomorrow."
]

# ========== JOB FETCH ==========
def fetch_jobs():
    jobs = []

    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    params = {
        "query": "software developer India",
        "page": "1",
        "num_pages": "2"
    }

    response = requests.get(url, headers=headers, params=params, timeout=20)
    data = response.json()

    print("Jobs received:", len(data.get("data", [])))

    for job in data.get("data", []):
        jobs.append({
            "title": job["job_title"],
            "company": job["employer_name"],
            "link": job["job_apply_link"]
        })

    return jobs[:15]

# ========== EMAIL ==========
def send_email(jobs):
    quote = random.choice(QUOTES)
    subject = f"🎯 Job Updates — {datetime.now().strftime('%d %b %Y')}"

    html = f"<h2>{quote}</h2><hr>"

    for job in jobs:
        html += f"""
        <p>
        <b>{job['title']}</b><br>
        {job['company']}<br>
        <a href="{job['link']}">Apply Now</a>
        </p>
        """

    for email in EMAIL_TO:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

    print("Emails sent successfully.")

# ========== MAIN ==========
if __name__ == "__main__":
    jobs = fetch_jobs()

    if jobs:
        send_email(jobs)
    else:
        send_email([{
            "title": "System Notice",
            "company": "No jobs found today",
            "link": "https://www.google.com"
        }])
