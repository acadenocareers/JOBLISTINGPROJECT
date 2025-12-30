import time, os
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO   = os.getenv("EMAIL_TO")

# ---------- Selenium Setup ----------
def start_browser():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

# ---------- Scrapers ----------
def scrape_site(driver, url, company):
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    jobs = []
    for a in soup.find_all("a"):
        title = " ".join(a.text.split())
        link = a.get("href", "")

        if len(title) > 10 and "job" in link.lower():
            if not link.startswith("http"):
                link = url.split("/")[0] + "//" + url.split("/")[2] + link
            jobs.append((company, title, link))

    return jobs

# ---------- Mail ----------
def send_email(jobs):
    subject = f"Kerala IT Job Updates — {datetime.now().strftime('%d %b %Y')}"

    body = "🎯 Today's Verified Kerala IT Openings\n\n"
    if not jobs:
        body += "⚠️ No jobs scraped today. Try again tomorrow."
    else:
        for c, t, l in jobs[:50]:
            body += f"🏢 {c}\n📌 {t}\n🔗 {l}\n\n"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

# ---------- Main ----------
if __name__ == "__main__":
    print("🚀 Scraping live Kerala IT job sites...")

    driver = start_browser()
    jobs = []

    jobs += scrape_site(driver, "https://infopark.in/companies/job-search", "Infopark")
    jobs += scrape_site(driver, "https://technopark.in/job-search", "Technopark")
    jobs += scrape_site(driver, "https://www.ulcyberpark.com/jobs", "Cyberpark")

    driver.quit()

    print("✅ Jobs collected:", len(jobs))
    send_email(jobs)
