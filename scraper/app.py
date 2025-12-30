import requests
import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

def get_technopark_jobs():
    url = "https://www.technopark.org/api/jobs"
    data = requests.get(url, headers=HEADERS).json()
    jobs = []

    for j in data:
        jobs.append(f"{j['title']} | {j['company']} | Technopark\n{j['url']}")

    return jobs

def get_infopark_jobs():
    url = "https://infopark.in/api/job/list"
    data = requests.get(url, headers=HEADERS).json()
    jobs = []

    for j in data['jobs']:
        jobs.append(f"{j['title']} | {j['company']} | Infopark\n{j['link']}")

    return jobs

def get_cyberpark_jobs():
    url = "https://www.cyberparkkerala.org/api/jobs"
    data = requests.get(url, headers=HEADERS).json()
    jobs = []

    for j in data:
        jobs.append(f"{j['title']} | {j['company']} | Cyberpark\n{j['apply_link']}")

    return jobs

def send_email(jobs):
    subject = f"Kerala IT Job Updates — {datetime.now().strftime('%d %b %Y')}"
    body = "\n\n".join(jobs) if jobs else "No jobs found today."

    msg = MIMEText(body)
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    print("📧 Mail sent successfully")

if __name__ == "__main__":
    print("🚀 Collecting Kerala IT jobs...")

    jobs = []
    jobs += get_technopark_jobs()
    jobs += get_infopark_jobs()
    jobs += get_cyberpark_jobs()

    print(f"✅ Total jobs found: {len(jobs)}")
    send_email(jobs)
