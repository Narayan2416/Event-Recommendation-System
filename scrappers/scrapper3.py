from playwright.sync_api import sync_playwright
import time
import pandas as pd
import re
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

BASE_URL = "https://www.eventbrite.com/d/india/technology-events/"
MAX_EVENTS = 2


# ---------------- DESCRIPTION ----------------
def extract_description(page):

    page.mouse.wheel(0, 5000)
    time.sleep(2)

    try:
        page.click("button[data-heap-id*='Read more']", timeout=2000)
    except:
        pass

    try:
        page.wait_for_selector("div.event-description", timeout=5000)
        text = page.locator("div.event-description").inner_text().strip()
        if len(text) > 30:
            return text
    except:
        pass

    return None


# ---------------- CITY ----------------
def extract_city(location_text):
    if not location_text:
        return None

    lines = location_text.split("\n")
    last_line = lines[-1]

    match = re.search(r"([A-Za-z ]+)(?=,)", last_line)
    if match:
        return match.group(0).strip()

    return None


# ---------------- MODE ----------------
def infer_mode(location_text):
    if not location_text:
        return "unknown"

    text = location_text.lower()
    if "online" in text:
        return "online"

    return "offline"


# ---------------- FEATURE EXTRACTION ----------------
def extract_event_features(page, event_url):

    # Title
    try:
        title = page.locator("h1").first.inner_text().strip()
    except:
        title = None

    # Date & Time
    start_datetime = None
    end_datetime = None
    try:
        times = page.locator("time").all_inner_texts()
        if len(times) >= 1:
            start_datetime = times[0]
        if len(times) >= 2:
            end_datetime = times[1]
    except:
        pass

    # Location
    location = None
    try:
        raw_location = page.locator("div[class*='locationInfo']").inner_text().strip()
        lines = [l.strip() for l in raw_location.split("\n") if l.strip()]

        cleaned_lines = []
        for line in lines:
            if "Show map" in line or "How do you want" in line:
                break
            cleaned_lines.append(line)

        # remove duplicates
        location = "\n".join(dict.fromkeys(cleaned_lines))

    except:
        location = None

    city = extract_city(location)
    mode = infer_mode(location)

    # Price
    price = "Unknown"
    try:
        price = page.locator("div[class*='priceTagWrapper']").inner_text().strip()
    except:
        try:
            price = page.locator("text=Free").first.inner_text()
        except:
            pass

    # Description
    description = extract_description(page)

    return {
        "title": title,
        "location": location,
        "city": city,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "mode": mode,
        "price": price,
        "description": description,
        "url": event_url
    }


# ---------------- MAIN ----------------
all_events = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # STEP 1: Collect event URLs
    page.goto(BASE_URL, timeout=60000)
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    links = page.query_selector_all("a[href*='/e/']")

    event_urls = []

    cards = page.locator("section:has-text('Just added')")

    for i in range(cards.count()):
        try:
            link = cards.nth(i).locator("a[href*='/e/']").first.get_attribute("href")

            if link:
                if link.startswith("/"):
                    link = "https://www.eventbrite.com" + link

                event_urls.append(link)

        except:
            pass

        if len(event_urls) >= MAX_EVENTS:
            break


    print(f"\nFound {len(event_urls)} events\n")

    # STEP 2: Extract features
    for idx, event_url in enumerate(event_urls):

        print(f"Processing {idx+1}/{len(event_urls)}")

        try:
            page.goto(event_url, timeout=60000)
            page.wait_for_load_state("networkidle")
            time.sleep(2)
        except:
            continue

        event_data = extract_event_features(page, event_url)
        all_events.append(event_data)

    browser.close()


# STEP 3: Print results
print("\nExtracted Events:\n")
pd.DataFrame(all_events).to_csv("extracted_events.csv", index=True)
for event in all_events:
    print(event)
    print("-" * 60)
