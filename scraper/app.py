import time, os
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import re

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
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

# ---------- Common Helper Functions ----------
def extract_job_info(element):
    """Extract job title and link from an element"""
    try:
        # Try to find title in various tags
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div', 'a']:
            title_elem = element.find(tag)
            if title_elem and title_elem.text.strip():
                title = title_elem.text.strip()
                break
        else:
            title = element.text.strip()[:100]  # Fallback
        
        # Try to find link
        link = ""
        link_elem = element.find('a', href=True)
        if link_elem:
            link = link_elem['href']
        elif element.name == 'a' and element.get('href'):
            link = element['href']
        
        return title, link if link else None
    except:
        return None, None

def is_job_related(text, link):
    """Check if text or link is job-related"""
    job_keywords = ['job', 'career', 'vacancy', 'opening', 'position', 'hire', 'recruit', 'apply', 'opportunity']
    text_lower = text.lower()
    link_lower = link.lower() if link else ""
    
    for keyword in job_keywords:
        if keyword in text_lower or keyword in link_lower:
            return True
    return False

# ---------- Scrapers for each site ----------
def scrape_infopark(driver):
    """Scrape Infopark job portal"""
    print("  Navigating to Infopark...")
    driver.get("https://infopark.in/companies/job-search")
    time.sleep(7)  # Increased wait time
    
    jobs = []
    
    try:
        # Try multiple selectors
        selectors = [
            (By.CLASS_NAME, "job-card"),
            (By.CLASS_NAME, "job-list-item"),
            (By.CLASS_NAME, "job-item"),
            (By.XPATH, "//*[contains(@class, 'job')]"),
            (By.XPATH, "//*[contains(text(), 'job') or contains(text(), 'Job')]//ancestor::div[1]"),
        ]
        
        for selector_type, selector_value in selectors:
            try:
                elements = driver.find_elements(selector_type, selector_value)
                if elements and len(elements) > 0:
                    print(f"  Found {len(elements)} elements with selector {selector_value}")
                    for element in elements:
                        html = element.get_attribute('outerHTML')
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Try to find all links in this element
                        links = soup.find_all('a', href=True)
                        for link_elem in links:
                            title = link_elem.text.strip()
                            link = link_elem['href']
                            
                            if title and len(title) > 5 and is_job_related(title, link):
                                if not link.startswith('http'):
                                    link = 'https://infopark.in' + link
                                jobs.append(("Infopark", title, link))
                    
                    if jobs:
                        break
            except:
                continue
        
        # Fallback: Get all links on page
        if not jobs:
            print("  Trying fallback: All links method")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            all_links = soup.find_all('a', href=True)
            
            for link_elem in all_links:
                title = link_elem.text.strip()
                link = link_elem['href']
                
                if title and len(title) > 10 and is_job_related(title, link):
                    if not link.startswith('http'):
                        link = 'https://infopark.in' + link
                    
                    # Check if it's a job listing page
                    if any(keyword in link.lower() for keyword in ['/job/', '/career/', '/vacancy/', '/apply']):
                        jobs.append(("Infopark", title, link))
    
    except Exception as e:
        print(f"  Error scraping Infopark: {e}")
    
    return jobs

def scrape_technopark(driver):
    """Scrape Technopark job portal"""
    print("  Navigating to Technopark...")
    driver.get("https://technopark.org/job-search")
    time.sleep(7)
    
    jobs = []
    
    try:
        # Save page source for debugging
        with open('technopark_debug.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        
        # Try to interact with the page
        try:
            # Look for search filters or buttons
            search_input = driver.find_elements(By.TAG_NAME, "input")
            for inp in search_input:
                if inp.get_attribute("placeholder") and "job" in inp.get_attribute("placeholder").lower():
                    inp.send_keys("software")
                    time.sleep(2)
                    break
        except:
            pass
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Try multiple strategies
        strategies = [
            # Strategy 1: Look for job containers
            lambda: soup.find_all(['div', 'tr', 'li'], class_=re.compile(r'job|listing|item', re.I)),
            # Strategy 2: Look for cards
            lambda: soup.find_all(['div', 'section'], class_=re.compile(r'card|panel|box', re.I)),
            # Strategy 3: Look for tables with job data
            lambda: soup.find_all('table'),
        ]
        
        for strategy in strategies:
            elements = strategy()
            if elements:
                print(f"  Found {len(elements)} potential job containers")
                for elem in elements:
                    # Extract text to check if it's job related
                    text = elem.get_text(strip=True)
                    if len(text) > 20 and is_job_related(text, ""):
                        # Find links in this element
                        links = elem.find_all('a', href=True)
                        for link_elem in links:
                            title = link_elem.text.strip() or text[:100]
                            link = link_elem['href']
                            
                            if title and link:
                                if not link.startswith('http'):
                                    link = 'https://technopark.org' + link
                                jobs.append(("Technopark", title, link))
                if jobs:
                    break
        
        # Fallback: Get all job-related links
        if not jobs:
            all_links = soup.find_all('a', href=True)
            for link_elem in all_links:
                title = link_elem.text.strip()
                link = link_elem['href']
                
                if title and len(title) > 8:
                    # Check if link looks like a job link
                    if any(keyword in link.lower() for keyword in ['/job', '/career', '/vacancy', '/apply', 'position']):
                        if not link.startswith('http'):
                            link = 'https://technopark.org' + link
                        jobs.append(("Technopark", title, link))
    
    except Exception as e:
        print(f"  Error scraping Technopark: {e}")
    
    return jobs

def scrape_cyberpark(driver):
    """Scrape Cyberpark job portal"""
    print("  Navigating to Cyberpark...")
    driver.get("https://www.ulcyberpark.com/jobs")
    time.sleep(7)
    
    jobs = []
    
    try:
        # Take screenshot for debugging
        driver.save_screenshot('cyberpark_debug.png')
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Strategy 1: Look for job listings
        job_patterns = [
            r'job.*list', r'career.*list', r'vacancy.*list',
            r'opening.*list', r'position.*list'
        ]
        
        for pattern in job_patterns:
            regex = re.compile(pattern, re.I)
            job_sections = soup.find_all(['div', 'section', 'ul'], class_=regex)
            
            for section in job_sections:
                # Find all links in this section
                links = section.find_all('a', href=True)
                for link_elem in links:
                    title = link_elem.text.strip()
                    link = link_elem['href']
                    
                    if title and len(title) > 5:
                        if not link.startswith('http'):
                            link = 'https://www.ulcyberpark.com' + link
                        jobs.append(("Cyberpark", title, link))
        
        # Strategy 2: Look for all job-related links
        if not jobs:
            all_links = soup.find_all('a', href=True)
            job_links = []
            
            for link_elem in all_links:
                title = link_elem.text.strip()
                link = link_elem['href']
                
                # Check if it's likely a job link
                is_likely_job = (
                    len(title) > 8 and 
                    (is_job_related(title, link) or 
                     any(keyword in link.lower() for keyword in ['/job/', '/career/', '/vacancy/', '/apply-', '/opening']))
                )
                
                if is_likely_job:
                    if not link.startswith('http'):
                        link = 'https://www.ulcyberpark.com' + link
                    job_links.append((title, link))
            
            # Remove duplicates
            seen = set()
            for title, link in job_links:
                if (title, link) not in seen:
                    seen.add((title, link))
                    jobs.append(("Cyberpark", title, link))
    
    except Exception as e:
        print(f"  Error scraping Cyberpark: {e}")
    
    return jobs

# ---------- Alternative: Use requests if possible ----------
def try_simple_requests():
    """Try using requests for static sites"""
    import requests
    
    jobs = []
    
    # Test URLs (some sites might have static versions)
    test_urls = [
        ("Infopark", "https://infopark.in/jobs"),
        ("Technopark", "https://technopark.org/jobs"),
    ]
    
    for company, url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)
                
                for link in links:
                    text = link.text.strip()
                    href = link['href']
                    
                    if text and len(text) > 10 and ('job' in text.lower() or 'career' in text.lower()):
                        if not href.startswith('http'):
                            href = url.split('/')[0] + '//' + url.split('/')[2] + href
                        jobs.append((company, text, href))
        except:
            continue
    
    return jobs

# ---------- Mail ----------
def send_email(jobs):
    subject = f"Kerala IT Job Updates — {datetime.now().strftime('%d %b %Y')}"
    
    body = "🎯 Today's Kerala IT Job Openings\n\n"
    
    if not jobs:
        body += "⚠️ No jobs scraped today.\n\n"
        body += "Troubleshooting steps:\n"
        body += "1. Check if websites are accessible\n"
        body += "2. Website structures may have changed\n"
        body += "3. Try running without --headless flag\n"
        body += "4. Check debug files created by script\n\n"
        body += "Test URLs:\n"
        body += "• https://infopark.in/companies/job-search\n"
        body += "• https://technopark.org/job-search\n"
        body += "• https://www.ulcyberpark.com/jobs\n"
    else:
        body += f"Found {len(jobs)} job postings:\n\n"
        for i, (company, title, link) in enumerate(jobs[:30], 1):  # Limit to 30
            body += f"{i}. {company}\n"
            body += f"   📝 {title}\n"
            body += f"   🔗 {link}\n\n"

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
        print(f"📧 Email sent with {len(jobs)} jobs")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

# ---------- Main ----------
if __name__ == "__main__":
    print("🚀 Starting Kerala IT Job Scraper...")
    print(f"📅 Date: {datetime.now().strftime('%d %b %Y %H:%M:%S')}\n")
    
    all_jobs = []
    
    # Try simple requests first (if sites are static)
    print("🔄 Trying simple HTTP requests...")
    simple_jobs = try_simple_requests()
    if simple_jobs:
        all_jobs.extend(simple_jobs)
        print(f"  Found {len(simple_jobs)} jobs via simple requests")
    
    # Use Selenium for dynamic sites
    print("\n🔄 Starting Selenium browser...")
    driver = None
    
    try:
        driver = start_browser()
        
        # Scrape each site
        print("\n🔍 Scraping Infopark...")
        infopark_jobs = scrape_infopark(driver)
        print(f"  ✓ Found {len(infopark_jobs)} jobs")
        
        print("\n🔍 Scraping Technopark...")
        technopark_jobs = scrape_technopark(driver)
        print(f"  ✓ Found {len(technopark_jobs)} jobs")
        
        print("\n🔍 Scraping Cyberpark...")
        cyberpark_jobs = scrape_cyberpark(driver)
        print(f"  ✓ Found {len(cyberpark_jobs)} jobs")
        
        all_jobs.extend(infopark_jobs + technopark_jobs + cyberpark_jobs)
        
    except Exception as e:
        print(f"❌ Main scraping error: {e}")
    finally:
        if driver:
            driver.quit()
        print("\n✅ Browser closed")
    
    # Remove duplicates
    unique_jobs = []
    seen = set()
    for company, title, link in all_jobs:
        # Create a unique key
        key = f"{company}_{title.lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append((company, title, link))
    
    print(f"\n📊 Total unique jobs: {len(unique_jobs)}")
    
    if unique_jobs:
        print("\n📋 Sample of jobs found:")
        for i, (company, title, link) in enumerate(unique_jobs[:5], 1):
            print(f"{i}. [{company}] {title[:60]}...")
            print(f"   Link: {link[:80]}...")
    else:
        print("\n❌ No jobs found. Creating debug files...")
        # Save current page sources for debugging
        if driver:
            try:
                with open('debug_page.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print("  Saved debug_page.html for inspection")
            except:
                pass
    
    # Send email
    print("\n📧 Sending email...")
    email_sent = send_email(unique_jobs)
    
    print(f"\n✨ Scraping complete! {'Email sent successfully!' if email_sent else 'Email failed.'}")