import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import subprocess

HEADERS = {"User-Agent": "Mozilla/5.0"}
JOBS_FILE = "jobs.json"

# ================== SCRAPERS ==================

def get_infopark():
    jobs = []
    url = "https://infopark.in/companies/job-search"
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find("table")
    if not table:
        return jobs

    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) >= 3:
            jobs.append({
                "park": "Infopark, Kochi",
                "date": cols[0].text.strip(),
                "title": cols[1].text.strip(),
                "company": cols[2].text.strip()
            })
    return jobs


def get_technopark():
    jobs = []
    url = "https://technopark.in/job-search"
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find("table")
    if not table:
        return jobs

    for row in table.find_all("tr")[1:]:
        cols = row.find_all("td")
        if len(cols) >= 3:
            jobs.append({
                "park": "Technopark, Trivandrum",
                "date": cols[0].text.strip(),
                "title": cols[1].text.strip(),
                "company": cols[2].text.strip()
            })
    return jobs


def get_cyberpark():
    jobs = []
    url = "https://www.ulcyberpark.com/jobs"
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.select("a"):
        text = a.get_text(strip=True)
        if len(text) > 12 and "job" in text.lower():
            jobs.append({
                "park": "Cyberpark, Kozhikode",
                "date": "",
                "title": text,
                "company": "Cyberpark Company"
            })
    return jobs


def get_tidel_park():
    jobs = []
    url = "https://www.tidelpark.com/careers"
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.select("a"):
        text = a.get_text(strip=True)
        if any(word in text.lower() for word in ["developer", "engineer", "analyst", "intern"]):
            jobs.append({
                "park": "TIDEL Park, Chennai",
                "date": "",
                "title": text,
                "company": "TIDEL Park"
            })
    return jobs

# ================== MAIN ==================

def main():
    all_jobs = []
    all_jobs += get_infopark()
    all_jobs += get_technopark()
    all_jobs += get_cyberpark()
    all_jobs += get_tidel_park()

    with open(JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(all_jobs)} jobs on {datetime.now()}")

# ================== AUTO PUSH ==================

def auto_git_push():
    subprocess.run(["git", "add", JOBS_FILE])
    subprocess.run(["git", "commit", "-m", "Auto update jobs"])
    subprocess.run(["git", "push"])

# ================== RUN ==================

if __name__ == "__main__":
    main()
    auto_git_push()
