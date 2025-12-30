import requests
import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ===================== ENV =====================

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ===================== CYBERPARK SCRAPER =====================

def get_cyberpark_jobs():
    url = "https://www.ulcyberpark.com/wp-json/wp/v2/job_listing?per_page=100"
    r = requests.get(url, headers=HEADERS, timeout=30)
    data = r.json()

    jobs = []
    for item in data:
        title = item["title"]["rendered"]
        link  = item["link"]

        jobs.append({
            "title": title,
            "company": "Cyberpark",
            "link": link
        })

    return jobs

# ===================== MAIL =====================

def send_email(jobs):
    subject = f"Kerala IT Job Updates — {datetime.now().strftime('%d %b %Y')}"

    if not jobs:
        body = "No jobs found today."
    else:
        body = ""
        for j in jobs:
            body += f"{j['title']}\n{j['company']}\n{j['link']}\n\n"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

# ===================== MAIN =====================

if __name__ == "__main__":
    jobs = get_cyberpark_jobs()
    print("Jobs found:", len(jobs))
    send_email(jobs)
