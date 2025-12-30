import os
import random
import smtplib
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO","").split(",")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

print("DEBUG EMAIL_USER:", EMAIL_USER)
print("DEBUG EMAIL_TO:", EMAIL_TO)
print("DEBUG API KEY PRESENT:", bool(RAPID_API_KEY))

KEYWORDS = [
    "python","full stack","data science","data analyst","power bi","tableau",
    "flask","digital marketing","flutter","frontend","react","html css"
]

QUOTES = [
    "Success is built one application at a time.",
    "Your future is created by what you do today.",
    "Great careers begin with brave applications."
]

def fetch_jobs():
    jobs = []
    for kw in KEYWORDS:
        url = "https://jsearch.p.rapidapi.com/search"
        headers = {
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        params = {
            "query": f"{kw} jobs in India",
            "page": "1",
            "num_pages": "1",
            "date_posted": "month",
            "experience": "under_5_years"
        }

        r = requests.get(url, headers=headers, params=params)
        data = r.json()
        print(f"DEBUG jobs for {kw}:", len(data.get("data", [])))

        for j in data.get("data", []):
            jobs.append({
                "title": j["job_title"],
                "company": j["employer_name"],
                "link": j["job_apply_link"]
            })
    return jobs[:20]

def send_email(jobs):
    quote = random.choice(QUOTES)
    subject = f"🎯 Job Updates — {datetime.now().strftime('%d %b %Y')}"
    html = f"<h2>{quote}</h2><hr>"

    for j in jobs:
        html += f"<b>{j['title']}</b><br>{j['company']}<br><a href='{j['link']}'>Apply</a><br><br>"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = ", ".join(EMAIL_TO)
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))

    print("DEBUG connecting SMTP…")
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
        server.set_debuglevel(1)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    print("DEBUG mail sent")

if __name__ == "__main__":
    jobs = fetch_jobs()
    print("DEBUG total jobs:", len(jobs))

    if jobs:
        send_email(jobs)
    else:
        print("DEBUG no jobs, skipping email")
