from playwright.sync_api import sync_playwright
import time
import re

BASE_URL = "https://www.eventbrite.com/d/india/technology-events/"

import json



def extract_structured_data(page):
    try:
        script_content = page.locator("script[type='application/ld+json']").first.inner_text()
        data = json.loads(script_content)

        title = data.get("name")
        description = data.get("description")
        start_datetime = data.get("startDate")
        end_datetime = data.get("endDate")

        location = None
        city = None

        if "location" in data:
            location = data["location"].get("name")
            address = data["location"].get("address", {})
            city = address.get("addressLocality")

        return title, location, city, start_datetime, end_datetime, description

    except Exception as e:
        print("Structured data extraction failed:", e)
        return None, None, None, None, None, None


# ---------------- DESCRIPTION ----------------
def extract_description(page):

    page.mouse.wheel(0, 5000)
    time.sleep(2)

    # click read more if present
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

    # common Indian cities detection
    cities = [
        "Bengaluru","Bangalore","Chennai","Coimbatore","Hyderabad",
        "Delhi","Mumbai","Pune","Kolkata","Ahmedabad"
    ]

    for c in cities:
        if c.lower() in location_text.lower():
            return c

    return None


# ---------------- MODE ----------------
def infer_mode(location_text):
    if not location_text:
        return "unknown"
    if "online" in location_text.lower():
        return "online"
    return "offline"


with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # ---------------- STEP 1: Get first event URL ----------------
    page.goto(BASE_URL, timeout=60000)
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    links = page.query_selector_all("a[href*='/e/']")
    
    event_url = None
 
    for link in links:
        href = link.get_attribute("href")
        title = link.inner_text().strip()
        if href and title:
            if href.startswith("/"):
                href = "https://www.eventbrite.com" + href
            event_url = href
            break

    if not event_url:
        print("No event found")
        browser.close()
        exit()

    print("\nOpening:", event_url)

    # ---------------- STEP 2: Open event page ----------------
    page.goto(event_url, timeout=60000)
    page.wait_for_load_state("networkidle")
    time.sleep(2)

    # scroll to load dynamic sections
    page.mouse.wheel(0, 4000)
    time.sleep(2)

    # ---------------- Extract Fields ----------------

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

    
    # Location extraction (cleaned)
    location = None
    try:
        raw_location = page.locator("div[class*='locationInfo']").inner_text().strip()

        # Split lines and keep meaningful ones
        lines = [l.strip() for l in raw_location.split("\n") if l.strip()]

        # Stop before "Show map" or directions
        cleaned_lines = []
        for line in lines:
            if "Show map" in line or "How do you want" in line:
                break
            cleaned_lines.append(line)

        location = "\n".join(cleaned_lines)

    except:
        location = None



    city = extract_city(location)
    mode = infer_mode(location)

    # Price (improved)
    price = "Unknown"

    try:
        page.wait_for_selector("div[class*='priceTagWrapper']", timeout=5000)
        price = page.locator("div[class*='priceTagWrapper']").inner_text().strip()
    except:
        pass


    # Description
    description = extract_description(page)

    browser.close()

# ---------------- PRINT ROW ----------------

row = {
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

print("\nExtracted Row:\n")
for k, v in row.items():
    print(f"{k}: {v}")
