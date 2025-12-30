import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from urllib.parse import urljoin

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ---------------- Utilities ----------------

def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def clean(txt):
    return " ".join(txt.split())

# ---------------- Scrapers ----------------

def get_infopark_jobs():
    soup = fetch("https://infopark.in/companies/job-search")
    jobs = []

    for card in soup.select("a[href*='/job/']"):
        title = clean(card.text)
        link = urljoin("https://infopark.in", card["href"])
        if len(title) > 8:
            jobs.append(("Infopark", title, link))

    return jobs

def get_technopark_jobs():
    soup = fetch("https://technopark.in/job-search")
    jobs = []

    for card in soup.select("a[href*='/job/']"):
        title = clean(card.text)
        link = urljoin("https://technopark.in", card["href"])
        if len(title) > 8:
            jobs.append(("Technopark", title, link))

    return jobs

def get_cyberpark_jobs():
    soup = fetch("https://www.ulcyberpark.com/jobs")
    jobs = []

    for card in soup.select("a[href]"):
        title = clean(card.text)
        href = card["href"]

        if "job" in title.lower() and len(title) > 8:
            link = urljoin("https://www.ulcyberpark.com", href)
            jobs.append(("Cyberpark", title, link))

    return jobs

# ---------------- Mailer ----------------

def send_email(jobs):
    subject = f"Kerala IT Job Updates — {datetime.now().strftime('%d %b %Y')}"
    
    body = "🎯 Today's Verified Kerala IT Openings\n\n"

    if not jobs:
        body += "⚠️ No jobs scraped today. Try again tomorrow."
    else:
        for company, title, link in jobs[:50]:
            body += f"🏢 {company}\n📌 {title}\n🔗 {link}\n\n"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    print("📧 Email sent with", len(jobs), "jobs.")

# ---------------- Main ----------------

if __name__ == "__main__":
    print("🚀 Collecting Kerala IT jobs...")

    jobs = []
    jobs += get_infopark_jobs()
    jobs += get_technopark_jobs()
    jobs += get_cyberpark_jobs()

    print("✅ Total jobs scraped:", len(jobs))
    send_email(jobs)
