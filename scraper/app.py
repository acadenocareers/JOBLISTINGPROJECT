import os
import smtplib
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ========== ENV ==========
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

print("DEBUG EMAIL_USER:", EMAIL_USER)
print("DEBUG EMAIL_TO:", EMAIL_TO)

# ========== SCRAPER ==========
def scrape_jobs():
    print("Starting scrape...")

    url = "https://www.naukri.com/jobs-in-india"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []
    cards = soup.select(".cust-job-tuple")

    print("Found job cards:", len(cards))

    for card in cards[:8]:   # only 8 jobs for test
        title = card.select_one(".title")
        company = card.select_one(".comp-name")
        link = title["href"] if title else None

        if title and company and link:
            jobs.append(f"{title.text.strip()} — {company.text.strip()}\n{link}")

    print("Scraped jobs:", len(jobs))
    return jobs

# ========== MAILER ==========
def send_mail(jobs):
    if not jobs:
        body = "No jobs scraped today."
    else:
        body = "\n\n".join(jobs)

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = f"Job Updates — {datetime.now().strftime('%d %b %Y')}"
    msg.attach(MIMEText(body, "plain"))

    print("Connecting to SMTP...")
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    print("Mail sent successfully.")

# ========== MAIN ==========
if __name__ == "__main__":
    jobs = scrape_jobs()
    send_mail(jobs)
