import os
import re
import time
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("FIRECRAWL_API_KEY")

QUERIES = [
    "Chipotle Mexican Grill investor relations press releases 2024",
    "Chipotle earnings results 2024",
    "Chipotle leadership team executives",
]

RESULTS_PER_QUERY = 3
OUT_DIR = "knowledge/raw"
os.makedirs(OUT_DIR, exist_ok=True)


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:60]


def search_and_save(query):
    response = requests.post(
        "https://api.firecrawl.dev/v1/search",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"query": query, "limit": RESULTS_PER_QUERY, "scrapeOptions": {"formats": ["markdown"]}},
    )
    response.raise_for_status()
    results = response.json().get("data", [])

    for item in results:
        url = item.get("url", "")
        markdown = item.get("markdown", "")
        if not markdown:
            continue
        filename = slugify(url) + ".md"
        filepath = os.path.join(OUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Source: {url}\n\n{markdown}")
        print(f"Saved: {filepath}")

    time.sleep(2)


for q in QUERIES:
    print(f"Searching: {q}")
    search_and_save(q)

print("Done!")