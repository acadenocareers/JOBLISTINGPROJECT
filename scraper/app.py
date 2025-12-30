import os
import requests
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO").split(",")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

QUOTES = [
    "Success is built one application at a time.",
    "Your future is created by what you do today.",
    "Great careers begin with brave applications.",
    "Opportunities don’t happen, you create them.",
    "Small steps today lead to big success tomorrow."
]

# ===================== SCRAPER =====================

def fetch_jobs():
    url = "https://jsearch.p.rapidapi.com/search"

    querystring = {
        "query": "Python Developer in India",
        "page": "1",
        "num_pages": "1"
    }

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    jobs = []
    for job in data.get("data", [])[:10]:
        jobs.append({
            "title": job["job_title"],
            "company": job["employer_name"],
            "link": job["job_apply_link"]
        })

    return jobs

# ===================== EMAIL =====================

def send_email(jobs):
    subject = f"🎯 Job Updates — {datetime.now().strftime('%d %b %Y')}"
    quote = random.choice(QUOTES)

    body = f"<h2>{quote}</h2><hr>"

    for job in jobs:
        body += f"""
        <p>
        <b>{job['title']}</b><br>
        {job['company']}<br>
        <a href="{job['link']}">Apply Now</a>
        </p>
        <hr>
        """

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(EMAIL_TO)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    print("Mail sent successfully!")

# ===================== MAIN =====================

if __name__ == "__main__":
    jobs = fetch_jobs()
    print(f"Jobs fetched: {len(jobs)}")
    send_email(jobs)
