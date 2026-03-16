from playwright.sync_api import sync_playwright
import time
import pandas as pd
import re
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')


BASE_URL = "https://www.eventbrite.com/d/india/technology-events/?page={}"
MAX_EVENTS = 300
MAX_PAGES = 15   # adjust if needed
cities = set(pd.read_csv("data/worldcities.csv")['city'].str.lower())
existing=pd.read_csv("data/event_data.csv")[['title','location','city','start_datetime','mode','price','description','url','price_type','embed_text','clean_desc']]
existing_urls = set(existing['url'].to_list())
existing_embeddings = np.load("data/event_embeddings2.npy")


# ---------------- DESCRIPTION ----------------
def extract_description(page):
    try:
        page.mouse.wheel(0, 5000)
        time.sleep(1)

        try:
            page.click("button:has-text('Read more')", timeout=2000)
        except:
            pass

        desc = page.locator("div.event-description").inner_text(timeout=5000)
        if desc and len(desc) > 30:
            return desc.strip()
    except:
        pass

    return None


# ---------------- CITY ----------------
def extract_city(location_text):
    if not location_text:
        return None

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

def normalize_price(price):
    if not isinstance(price, str):
        return "unknown"

    p = price.lower()
    if "sales ended" in p:
        return "unknown"
    if "free" in p and "paid" in p:
        return "mixed"
    if "free" in p:
        return "free"
    if "paid" in p or "$" in p or "₹" in p or "€" in p or "£" in p:
        return "paid"
    return "unknown"




def preprocess(df):
    if df.empty:
        return

    df["clean_desc"] = df["description"].apply(clean_text)
    df["price_type"] = df["price"].apply(normalize_price)
    df['embed_text'] = (
        df['title'].fillna('') + " " +
        df['clean_desc'].fillna('') + " " +
        df['city'].fillna('') + " " +
        df['mode'].fillna('') + " " +
        df['price_type'].fillna('')
    )

    df=pd.concat([existing, df], ignore_index=True)
    df = df.drop_duplicates(subset="url")

    texts = ["passage: " + t for t in df["embed_text"].tolist()]
    embeddings = model.encode(texts, show_progress_bar=True)
    df.to_csv("event_data.csv", index=True)
    np.save("event_embeddings2.npy", embeddings)
    df.to_json("extracted_events.json", orient="records", indent=2)
    return df.to_dict(orient="records")

def clean_text(text):
    if not isinstance(text, str):
        return ""

    # remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)

    # remove phone numbers
    text = re.sub(r'\+?\d[\d\s\-]{8,}', '', text)

    # remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()
     



# ---------------- MAIN ----------------
def add_new_Event():
    all_events = []
    event_urls = []

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Collecting event links...")

        # -------- STEP 1: URL PAGINATION --------
        for page_num in range(1, MAX_PAGES + 1):

            url = BASE_URL.format(page_num)
            print(f"\nOpening page {page_num}")

            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
            time.sleep(2)

            links = page.query_selector_all("a[href*='/e/']")
            print("Events found:", len(links))

            # Stop if no events
            if len(links) == 0:
                print("No more events found.")
                break

            for link in links:
                href = link.get_attribute("href")

                if href:
                    if href.startswith("/"):
                        href = "https://www.eventbrite.com" + href

                    href = href.split("?")[0]
                    if href not in event_urls and href not in existing_urls:
                        event_urls.append(href)

                if len(event_urls) >= MAX_EVENTS:
                    break

            print("Total collected:", len(event_urls))

            if len(event_urls) >= MAX_EVENTS:
                break

        print(f"\nTotal URLs collected: {len(event_urls)}\n")

        # -------- STEP 2: VISIT EVENT PAGES --------
        for idx, event_url in enumerate(event_urls):

            print(f"Processing {idx+1}/{len(event_urls)}")

            try:
                page.goto(event_url, timeout=60000)
                page.wait_for_load_state("networkidle")
                time.sleep(2)
            except:
                continue

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

                location = "\n".join(cleaned_lines)

            except:
                location = None

            city = extract_city(location)
            mode = infer_mode(location)

            # Price
            price = "Unknown"
            try:
                price = page.locator("div[class*='priceTagWrapper']").inner_text(timeout=5000)
            except:
                pass

            # Description
            description = extract_description(page)

            # Save row
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

            all_events.append(row)

        browser.close()



    # -------- STEP 3: SAVE OUTPUT --------
    df = pd.DataFrame(all_events)
    return preprocess(df)
