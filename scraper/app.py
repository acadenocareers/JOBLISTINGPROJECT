import os
import smtplib
import time
import random
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import requests

# ========== EMAIL CONFIG ==========
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO").split(",")

# ========== MOTIVATION QUOTES ==========
QUOTES = [
    "Success is built one application at a time.",
    "Your future is created by what you do today.",
    "Great careers begin with brave applications.",
    "Opportunities don’t happen, you create them.",
    "Small steps today lead to big success tomorrow."
]

# ========== JOB SCRAPER ==========
def scrape_jobs():
    print("Starting job scraping...")
    url = "https://www.indeed.com/jobs?q=python&l=India"

    try:
        response = requests.get(url, timeout=20)
        soup = BeautifulSoup(response.text, "html.parser")
    except:
        return []

    jobs = []
    for card in soup.select(".result")[:6]:
        title = card.select_one("h2")
        company = card.select_one(".companyName")
        link = card.select_one("a")

        if title and company and link:
            jobs.append({
                "title": title.text.strip(),
                "company": company.text.strip(),
                "link": "https://www.indeed.com" + link["href"]
            })

    print("Jobs found:", len(jobs))
    return jobs

# ========== EMAIL SENDER ==========
def send_emails(jobs):
    quote = random.choice(QUOTES)
    subject = f"🎯 Job Updates — {datetime.now().strftime('%d %b %Y')}"

    for email in EMAIL_TO:
        html = f"""
        <h2>{quote}</h2>
        <hr>
        """

        for job in jobs:
            html += f"""
            <div style="margin-bottom:12px">
                <b>{job['title']}</b><br>
                {job['company']}<br>
                <a href="{job['link']}">Apply Now</a>
            </div>
            """

        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(html, "html"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()

        print("Email sent to", email)

# ========== MAIN ==========
def main():
    jobs = scrape_jobs()

    # Always send mail (even if scraping blocked)
    if not jobs:
        jobs = [{
            "title": "⚠️ No jobs scraped today",
            "company": "System Status",
            "link": "https://www.indeed.com"
        }]

    send_emails(jobs)

if __name__ == "__main__":
    main()
