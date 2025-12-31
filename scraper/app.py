import requests, json, time
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {"User-Agent": "Mozilla/5.0"}

JOBS_FILE = "jobs.json"


def get_infopark():
    jobs = []
    url = "https://infopark.in/companies/job-search"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")


    table = soup.find("table")
    if not table:
        return jobs

    rows = table.find_all("tr")[1:]
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 3:
            jobs.append({
                "park": "Infopark",
                "date": cols[0].text.strip(),
                "title": cols[1].text.strip(),
                "company": cols[2].text.strip()
            })
    return jobs

def main():
    all_jobs = []
    all_jobs += get_infopark()

    with open(JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(all_jobs)} jobs on {datetime.now()}")

if __name__ == "__main__":
    main()
