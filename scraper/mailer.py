import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

# ====== ENV VARIABLES FROM GITHUB SECRETS ======
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

JOBS_FILE = "scraper/jobs.json"

def load_jobs():
    if not os.path.exists(JOBS_FILE):
        return []
    with open(JOBS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def format_mail(jobs):
    today = datetime.now().strftime("%d %b %Y")
    subject = f"🧑‍💻 Daily IT Job Updates — {today}"

    body = f"Hello,\n\nHere are today's latest job openings:\n\n"

    for job in jobs[:40]:
        body += f"""
🔹 {job.get('title')}
🏢 {job.get('company')}
📍 {job.get('park')}
🗓 {job.get('date')}

"""

    body += "\nBest of luck!\nYour Job Tracker 🤖"

    return subject, body

def send_mail(subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    print("✅ Mail sent successfully")

def main():
    jobs = load_jobs()
    if not jobs:
        print("⚠️ No jobs found. Mail not sent.")
        return

    subject, body = format_mail(jobs)
    send_mail(subject, body)

if __name__ == "__main__":
    main()
