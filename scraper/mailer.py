import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

def send_job_email(jobs):
    today = datetime.now().strftime("%d %b %Y")

    subject = f"Kerala IT Job Updates — {today}"

    if not jobs:
        body = "⚠ No jobs scraped today. Try again tomorrow."
    else:
        body = f"Hello 👋\n\nHere are today's verified IT job openings:\n\n"

        parks = {}
        for job in jobs:
            park = job.get("park", "Other")
            parks.setdefault(park, []).append(job)

        for park, park_jobs in parks.items():
            body += f"{park}:\n"
            for job in park_jobs:
                body += f"• {job['title']} — {job['company']}\n"
            body += "\n"

        body += f"Total jobs found: {len(jobs)}\n\n"
        body += "Good luck with your applications 🍀\n\n"
        body += "— Automated Job Scraper System"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

    print("📧 Email sent successfully! ")
