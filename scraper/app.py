import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import subprocess
from urllib.parse import quote_plus

HEADERS = {"User-Agent": "Mozilla/5.0"}
JOBS_FILE = "jobs.json"

# ================== HELPERS ==================

def build_fallback_link(title, company):
    query = quote_plus(f"{title} {company}")
    return f"https://www.google.com/search?q={query}"

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
            title_cell = cols[1]
            link_tag = title_cell.find("a")

            title = title_cell.text.strip()
            company = cols[2].text.strip()

            job_link = ""
            if link_tag and link_tag.get("href"):
                job_link = "https://infopark.in" + link_tag["href"]

            if not job_link:
                job_link = build_fallback_link(title, company)

            jobs.append({
                "park": "Infopark, Kochi",
                "date": cols[0].text.strip(),
                "title": title,
                "company": company,
                "link": job_link
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
            title_cell = cols[1]
            link_tag = title_cell.find("a")

            title = title_cell.text.strip()
            company = cols[2].text.strip()

            job_link = ""
            if link_tag and link_tag.get("href"):
                job_link = "https://technopark.in" + link_tag["href"]

            if not job_link:
                job_link = build_fallback_link(title, company)

            jobs.append({
                "park": "Technopark, Trivandrum",
                "date": cols[0].text.strip(),
                "title": title,
                "company": company,
                "link": job_link
            })

    return jobs


def get_cyberpark():
    jobs = []
    url = "https://www.ulcyberpark.com/jobs"

    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.select("a"):
        title = a.get_text(strip=True)
        href = a.get("href", "")

        if len(title) > 12 and "job" in title.lower():
            company = "Cyberpark Company"

            job_link = href if href.startswith("http") else "https://www.ulcyberpark.com" + href
            if not href:
                job_link = build_fallback_link(title, company)

            jobs.append({
                "park": "Cyberpark, Kozhikode",
                "date": "",
                "title": title,
                "company": company,
                "link": job_link
            })

    return jobs


def get_tidel_park():
    jobs = []
    url = "https://www.tidelpark.com/careers"

    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.select("a"):
        title = a.get_text(strip=True)
        href = a.get("href", "")

        if any(word in title.lower() for word in ["developer", "engineer", "analyst", "intern"]):
            company = "TIDEL Park"

            job_link = href if href.startswith("http") else "https://www.tidelpark.com" + href
            if not href:
                job_link = build_fallback_link(title, company)

            jobs.append({
                "park": "TIDEL Park, Chennai",
                "date": "",
                "title": title,
                "company": company,
                "link": job_link
            })

    return jobs

# ================== MAIN ==================

def main():
    all_jobs = []
    all_jobs += get_infopark()
    all_jobs += get_technopark()
    all_jobs += get_cyberpark()
    all_jobs += get_tidel_park()

    # Remove duplicates
    unique = {(job["title"], job["company"], job["link"]): job for job in all_jobs}
    all_jobs = list(unique.values())

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
