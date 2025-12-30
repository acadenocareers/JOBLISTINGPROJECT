import os
import random
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

print("🔹 Script started")

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

RAPID_API_KEY = os.getenv("RAPID_API_KEY")

print("🔹 ENV CHECK:")
print("EMAIL_USER:", EMAIL_USER)
print("EMAIL_TO:", EMAIL_TO)
print("API KEY FOUND:", bool(RAPID_API_KEY))

if not EMAIL_USER or not EMAIL_PASS or not EMAIL_TO:
    raise Exception("❌ Missing email configuration in GitHub Secrets")

EMAIL_TO = EMAIL_TO.split(",")

QUOTES = [
    "Success is built one application at a time.",
    "Your future is created by what you do today.",
    "Great careers begin with brave applications.",
    "Opportunities don’t happen, you create them."
]

# ---------------- FETCH JOBS ----------------

def fetch_jobs():
    jobs = []

    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    params = {"query": "IT jobs India", "page": "1", "num_pages": "2"}

    r = requests.get(url, headers=headers, params=params, timeout=15)
    data = r.json()

    print(f"🔹 Jobs fetched: {len(data.get('data', []))}")

    for job in data.get("data", []):
        jobs.append({
            "title": job["job_title"],
            "company": job["employer_name"],
            "link": job["job_apply_link"]
        })

    return jobs[:15]

# ---------------- SEND EMAIL ----------------

def send_email(jobs):
    print("🔹 Sending email...")

    quote = random.choice(QUOTES)
    subject = f"🎯 Job Updates — {datetime.now().strftime('%d %b %Y')}"

    html = f"<h2>{quote}</h2><hr>"

    if not jobs:
        html += "<p><b>No jobs found today.</b></p>"

    for job in jobs:
        html += f"""
        <div>
        <b>{job['title']}</b><br>
        {job['company']}<br>
        <a href="{job['link']}">Apply</a>
        </div><br>
        """

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(EMAIL_TO)
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    print("✅ Email sent")

# ---------------- MAIN ----------------

jobs = fetch_jobs()
send_email(jobs)
print("🎉 Script completed")
