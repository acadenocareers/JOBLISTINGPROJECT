import time, re, os
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ------------------ CONFIG ------------------

TECH_KEYWORDS = [
    "python","data","analyst","analytics","power bi","tableau",
    "machine learning","ai","full stack","developer","engineer",
    "intern","trainee","react","django","flask","frontend","backend","flutter"
]

EXCLUDE = ["php","laravel","wordpress",".net","c#","java","senior","lead","manager","architect"]

# ------------------ BROWSER ------------------

def start_browser():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ------------------ FILTER ------------------

def relevant(title):
    t = title.lower()
    if any(x in t for x in EXCLUDE): return False
    return any(x in t for x in TECH_KEYWORDS)

# ------------------ SCRAPERS ------------------

def scrape_infopark(driver):
    jobs=[]
    for page in range(1,6):
        url=f"https://infopark.in/companies/job-search?page={page}"
        driver.get(url); time.sleep(2)
        soup=BeautifulSoup(driver.page_source,"html.parser")
        rows=soup.select("table tr")[1:]
        for r in rows:
            c=r.find_all("td")
            if len(c)<3: continue
            title=c[1].text.strip()
            company=c[2].text.strip()
            link=r.find("a")["href"]
            if relevant(title):
                jobs.append(("Infopark",title,company,"https://infopark.in"+link))
    return jobs

def scrape_technopark(driver):
    jobs=[]
    driver.get("https://technopark.in/job-search")
    time.sleep(3)
    soup=BeautifulSoup(driver.page_source,"html.parser")
    for a in soup.select("a"):
        title=a.text.strip()
        href=a.get("href","")
        if "/job/" in href and relevant(title):
            jobs.append(("Technopark",title,"Company","https://technopark.in"+href))
    return jobs

def scrape_cyberpark(driver):
    jobs=[]
    driver.get("https://cyberparkkerala.org/careers")
    time.sleep(3)
    text=driver.find_element("tag name","body").text.split("\n")
    for line in text:
        if relevant(line):
            jobs.append(("Cyberpark",line,"Company","https://cyberparkkerala.org/careers"))
    return jobs

# ------------------ MAIN ------------------

if __name__ == "__main__":
    driver=start_browser()
    all_jobs=[]
    
    all_jobs+=scrape_infopark(driver)
    all_jobs+=scrape_technopark(driver)
    all_jobs+=scrape_cyberpark(driver)

    driver.quit()

    print(f"\nTOTAL JOBS FOUND: {len(all_jobs)}\n")

    for park,title,company,link in all_jobs:
        print(f"{park} | {title} | {company}")
        print(link,"\n")

    with open("jobs.txt","w",encoding="utf-8") as f:
        for j in all_jobs:
            f.write(" | ".join(j)+"\n")

    print("Saved to jobs.txt")
