import time, os
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=options)

# ---------- Scrapers for each site ----------
def scrape_infopark(driver):
    """Scrape Infopark job portal"""
    driver.get("https://infopark.in/companies/job-search")
    time.sleep(5)
    
    # Try to wait for job listings to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "job-card"))
        )
    except:
        print("Infopark: Job cards not found, trying alternative selectors...")
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    jobs = []
    
    # Updated selectors for Infopark
    job_cards = soup.find_all("div", class_="job-card")
    if not job_cards:
        # Alternative selectors
        job_cards = soup.find_all("div", class_="job-list-item")
    
    for card in job_cards:
        title_elem = card.find("h3") or card.find("h4") or card.find("a", class_="job-title")
        if title_elem:
            title = title_elem.text.strip()
            # Find link
            link_elem = card.find("a", href=True)
            if link_elem:
                link = link_elem["href"]
                if not link.startswith("http"):
                    link = "https://infopark.in" + link
                
                if title and link:
                    jobs.append(("Infopark", title, link))
    
    # Fallback to generic search if no jobs found
    if not jobs:
        for a in soup.find_all("a", href=True):
            title = a.text.strip()
            link = a["href"]
            if title and len(title) > 10 and ("job" in title.lower() or "career" in title.lower()):
                if not link.startswith("http"):
                    link = "https://infopark.in" + link
                jobs.append(("Infopark", title, link))
    
    return jobs

def scrape_technopark(driver):
    """Scrape Technopark job portal"""
    driver.get("https://technopark.in/job-search")
    time.sleep(5)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "job-item"))
        )
    except:
        print("Technopark: Job items not found, trying alternative selectors...")
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    jobs = []
    
    # Look for job listings
    job_items = soup.find_all("div", class_="job-item")
    if not job_items:
        job_items = soup.find_all("tr", class_="job-row")
    
    for item in job_items:
        # Try different selectors for title
        title_elem = (item.find("h3") or item.find("h4") or 
                     item.find("a", class_="job-title") or 
                     item.find("td", class_="job-title"))
        
        if title_elem:
            title = title_elem.text.strip()
            link_elem = item.find("a", href=True)
            
            if link_elem:
                link = link_elem["href"]
                if not link.startswith("http"):
                    link = "https://technopark.in" + link
                
                if title and link:
                    jobs.append(("Technopark", title, link))
    
    # Fallback
    if not jobs:
        for a in soup.find_all("a", href=True):
            if "job" in a.get("href", "").lower() or "apply" in a.get("href", "").lower():
                title = a.text.strip()
                link = a["href"]
                if title and len(title) > 5:
                    if not link.startswith("http"):
                        link = "https://technopark.in" + link
                    jobs.append(("Technopark", title, link))
    
    return jobs

def scrape_cyberpark(driver):
    """Scrape Cyberpark job portal"""
    driver.get("https://www.ulcyberpark.com/jobs")
    time.sleep(5)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "job-listing"))
        )
    except:
        print("Cyberpark: Job listings not found, trying alternative selectors...")
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    jobs = []
    
    # Look for job listings - Cyberpark might use different structure
    job_listings = soup.find_all("div", class_="job-listing")
    if not job_listings:
        job_listings = soup.find_all("article", class_="job")
    
    for listing in job_listings:
        title_elem = listing.find("h2") or listing.find("h3")
        if title_elem:
            title = title_elem.text.strip()
            link_elem = listing.find("a", href=True)
            
            if link_elem:
                link = link_elem["href"]
                if not link.startswith("http"):
                    link = "https://www.ulcyberpark.com" + link
                
                if title and link:
                    jobs.append(("Cyberpark", title, link))
    
    # Fallback for Cyberpark
    if not jobs:
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/job/" in href or "/career/" in href or "/vacancy/" in href:
                title = a.text.strip()
                link = href
                if title and len(title) > 5:
                    if not link.startswith("http"):
                        link = "https://www.ulcyberpark.com" + link
                    jobs.append(("Cyberpark", title, link))
    
    return jobs

# ---------- Mail ----------
def send_email(jobs):
    subject = f"Kerala IT Job Updates — {datetime.now().strftime('%d %b %Y')}"
    
    body = "🎯 Today's Verified Kerala IT Openings\n\n"
    if not jobs:
        body += "⚠️ No jobs scraped today. Check if website structures have changed.\n\n"
        body += "Potential issues:\n"
        body += "1. Websites might have updated their HTML structure\n"
        body += "2. Some sites might require JavaScript interaction\n"
        body += "3. Access might be blocked (check if you can access manually)\n"
    else:
        for company, title, link in jobs[:50]:  # Limit to 50 jobs
            body += f"🏢 {company}\n📌 {title}\n🔗 {link}\n{'─'*50}\n\n"

    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print(f"📧 Email sent successfully with {len(jobs)} jobs")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# ---------- Main ----------
if __name__ == "__main__":
    print("🚀 Scraping live Kerala IT job sites...")
    print(f"📅 {datetime.now().strftime('%d %b %Y %H:%M:%S')}\n")
    
    driver = start_browser()
    all_jobs = []
    
    try:
        print("🔍 Scraping Infopark...")
        infopark_jobs = scrape_infopark(driver)
        print(f"   Found {len(infopark_jobs)} jobs")
        all_jobs.extend(infopark_jobs)
        
        print("🔍 Scraping Technopark...")
        technopark_jobs = scrape_technopark(driver)
        print(f"   Found {len(technopark_jobs)} jobs")
        all_jobs.extend(technopark_jobs)
        
        print("🔍 Scraping Cyberpark...")
        cyberpark_jobs = scrape_cyberpark(driver)
        print(f"   Found {len(cyberpark_jobs)} jobs")
        all_jobs.extend(cyberpark_jobs)
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
    finally:
        driver.quit()
    
    # Remove duplicates (same title and company)
    unique_jobs = []
    seen = set()
    for company, title, link in all_jobs:
        key = (company, title.lower())
        if key not in seen:
            seen.add(key)
            unique_jobs.append((company, title, link))
    
    print(f"\n✅ Total unique jobs collected: {len(unique_jobs)}")
    
    if unique_jobs:
        print("\n📋 Sample jobs:")
        for i, (company, title, link) in enumerate(unique_jobs[:3], 1):
            print(f"{i}. {company}: {title[:60]}...")
    
    send_email(unique_jobs)
    print("\n✨ Scraping complete!")