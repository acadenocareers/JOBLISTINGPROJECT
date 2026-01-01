import time, re, json, subprocess
import pandas as pd
from bs4 import BeautifulSoup
import requests
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

JOBS_FILE = "jobs.json"

# =========================================================
# DRIVER (STEALTH + HEADLESS + CRASH SAFE)
# =========================================================

def create_driver():
    chrome_options = Options()

    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                            options=chrome_options)

driver = create_driver()

# =========================================================
# HELPERS
# =========================================================

def scroll_page(times=10, pause=1.2):
    for _ in range(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)

# =========================================================
# FILTERS
# =========================================================

EXCLUDE = ["php","laravel","wordpress","drupal",".net","c#","java","spring","hibernate",
           "senior","lead","manager","architect","director","principal","vp","head",
           "3 year","4 year","5 year","6 year","7 year"]

INCLUDE = ["python","django","flask","fastapi","react","angular","vue","javascript",
           "full stack","backend","frontend","machine learning","ml","ai",
           "data","analyst","power bi","tableau","sql","nlp","llm","pandas",
           "numpy","tensorflow","pytorch"]

HIGH_EXP = re.compile(r"\b([3-9]|[1-9]\d)\+?\s*(year|years)\b", re.I)

def looks_relevant(title):
    t = title.lower()
    if any(x in t for x in EXCLUDE): return False
    if not any(x in t for x in INCLUDE): return False
    if re.search(HIGH_EXP, t): return False
    return True

def is_valid_job_link(link):
    if not link: return False
    bad = ["#","javascript","mailto","/blog","/en/","/main","/infrastructure",
           "/land","campaign","webmail"]
    return not any(b in link.lower() for b in bad)

# =========================================================
# NETWORK SAFE GET
# =========================================================

def safe_get(url, retries=3):
    global driver
    for i in range(retries):
        try:
            driver.get(url)
            time.sleep(2)
            return BeautifulSoup(driver.page_source,"html.parser")
        except:
            print(f"⚠️ Load failed {i+1}/{retries} → {url}")
            try: driver.quit()
            except: pass
            time.sleep(2)
            driver = create_driver()
    return None

# =========================================================
# DEDUPE
# =========================================================

def dedupe(jobs):
    seen=set(); out=[]
    for j in jobs:
        k=(j["title"].lower(), j["link"])
        if k not in seen:
            seen.add(k); out.append(j)
    return out

# =========================================================
# SCRAPERS (ALL WEBSITES)
# =========================================================

def fetch_infopark(pages=6):
    jobs=[]
    for p in range(1,pages+1):
        soup=safe_get(f"https://infopark.in/companies/job-search?page={p}")
        if not soup: continue
        for r in soup.select("table tr")[1:]:
            c=r.find_all("td")
            if len(c)<3: continue
            title=c[1].text.strip()
            link="https://infopark.in"+r.find("a")["href"]
            if looks_relevant(title):
                jobs.append({"title":title,"link":link})
    return jobs

def fetch_technopark(pages=5):
    jobs=[]
    for _ in range(pages):
        soup=safe_get("https://technopark.in/job-search")
        if not soup: continue
        scroll_page()
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for card in soup.select('a[href^="/job-details"]'):
            title_el = card.select_one("h4.bodyemphasis")
            if not title_el: continue
            title = title_el.get_text(strip=True)
            link = "https://technopark.in" + card["href"]
            if looks_relevant(title):
                jobs.append({"title": title, "link": link})
    return jobs

def fetch_cyberpark():
    jobs=[]
    soup=safe_get("https://cyberparks.in/careers")
    if not soup: return jobs
    for a in soup.select("a[href*='/job/']"):
        title = a.text.strip()
        link=a["href"]
        if looks_relevant(title) and is_valid_job_link(link):
            jobs.append({"title":title,"link":link})
    return jobs

def fetch_smartcity():
    jobs=[]
    soup=BeautifulSoup(requests.get("https://smartcity-kochi.in/media-hub/job-openings/",timeout=15).text,"html.parser")
    for article in soup.select("article"):
        t=article.select_one("h2 a")
        if not t: continue
        title=t.text.strip()
        link=t["href"]
        if looks_relevant(title):
            jobs.append({"title":title,"link":link})
    return jobs

def fetch_tidel():
    jobs=[]
    soup=safe_get("https://www.tidelpark.com/careers")
    if not soup: return jobs
    for a in soup.select("a[href*='career'], a[href*='job']"):
        title=a.text.strip()
        link=a["href"]
        if looks_relevant(title) and is_valid_job_link(link):
            jobs.append({"title":title,"link":link})
    return jobs

def fetch_stpi():
    jobs=[]
    soup=safe_get("https://www.stpi.in/career")
    if not soup: return jobs
    for a in soup.select("a[href*='career'], a[href*='job']"):
        title=a.text.strip()
        link=a["href"]
        if looks_relevant(title) and is_valid_job_link(link):
            jobs.append({"title":title,"link":link})
    return jobs

def fetch_indeed(pages=3):
    jobs=[]
    for p in range(pages):
        soup=safe_get(f"https://www.indeed.co.in/jobs?q=python+data+analyst&start={p*10}")
        if not soup: continue
        for c in soup.select("a.tapItem"):
            title=c.select_one("h2").text.strip()
            link="https://www.indeed.co.in"+c["href"]
            if looks_relevant(title):
                jobs.append({"title":title,"link":link})
    return jobs

# =========================================================
# MAIN
# =========================================================

print("\n🌀 Starting FULL job scraping engine...\n")

jobs=[]
jobs+=fetch_infopark()
jobs+=fetch_technopark()
jobs+=fetch_cyberpark()
jobs+=fetch_smartcity()
jobs+=fetch_tidel()
jobs+=fetch_stpi()
jobs+=fetch_indeed()

jobs=dedupe(jobs)

pd.DataFrame(jobs).to_csv("jobs.csv",index=False)

with open(JOBS_FILE,"w",encoding="utf-8") as f:
    json.dump(jobs,f,indent=2)

driver.quit()

print(f"\n✅ Completed — {len(jobs)} jobs saved to jobs.csv & jobs.json\n")

# =========================================================
# AUTO PUSH
# =========================================================

subprocess.run(["git","add","jobs.csv",JOBS_FILE])
subprocess.run(["git","commit","-m","Auto update jobs with verified application links"])
subprocess.run(["git","push"])
