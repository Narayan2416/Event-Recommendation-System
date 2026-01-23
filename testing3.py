from playwright.sync_api import sync_playwright, TimeoutError
import pandas as pd
import time

BASE_URL = "https://www.eventbrite.com/d/india/technology-events/"
MAX_PAGES = 25          # pagination limit
DETAIL_TIMEOUT = 45000  # ms
SCROLL_WAIT = 2

# ------------------ helpers ------------------

def extract_description(page):
    """
    Try multiple known layouts for Eventbrite descriptions.
    Returns text or None.
    """
    selectors = [
        "[data-testid='structured-description']",
        "section[aria-label='Event description']",
        "div[data-automation='listing-event-description']",
        "section:has(h2:has-text('About this event'))"
    ]

    for sel in selectors:
        try:
            page.wait_for_selector(sel, timeout=5000)
            text = page.locator(sel).inner_text().strip()
            if len(text) > 50:
                return text
        except:
            continue

    return None


def infer_is_free(price_text):
    if not price_text:
        return None
    p = price_text.lower()
    return any(x in p for x in ["free", "₹0", "no cost"])


def infer_mode(location_text):
    if not location_text:
        return "unknown"
    return "online" if "online" in location_text.lower() else "offline"


def safe_goto(page, url):
    """
    Retry navigation once if it fails.
    """
    for _ in range(2):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=DETAIL_TIMEOUT)
            page.wait_for_selector("h1", timeout=15000)
            return True
        except:
            time.sleep(2)
    return False


# ------------------ main ------------------

events_basic = []   # stage 1
events_full = []    # stage 2

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # ---------- STAGE 1: PAGINATION ----------
    print("\n🔹 Stage 1: Collecting event URLs")

    for page_no in range(1, MAX_PAGES + 1):
        url = f"{BASE_URL}?page={page_no}"
        print(f"Page {page_no}: {url}")

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except TimeoutError:
            print("  ⚠️ Page timeout, skipping")
            continue

        time.sleep(2)

        # accept cookies once
        try:
            page.click("button:has-text('Accept')", timeout=3000)
        except:
            pass

        links = page.query_selector_all("a[href*='/e/']")

        if not links:
            print("  ❌ No more events, stopping pagination")
            break

        for link in links:
            try:
                title = link.inner_text().strip()
                href = link.get_attribute("href")
                if title and href:
                    events_basic.append({
                        "title": title,
                        "url": href
                    })
            except:
                pass

    print(f"\nCollected {len(events_basic)} event URLs")

    # deduplicate
    df_basic = pd.DataFrame(events_basic).drop_duplicates(subset=["url"])

    # ---------- STAGE 2: EVENT DETAILS ----------
    print("\n🔹 Stage 2: Extracting event details")

    for i, row in df_basic.iterrows():
        url = row["url"]
        print(f"[{i+1}/{len(df_basic)}] {url}")

        if not safe_goto(page, url):
            print("  ⚠️ Skipping (navigation failed)")
            continue

        time.sleep(2)

        # TITLE
        try:
            title = page.locator("h1").first.inner_text().strip()
        except:
            title = row["title"]

        # DATE / TIME
        try:
            datetime = page.locator("time").first.inner_text().strip()
        except:
            datetime = None

        # LOCATION
        try:
            location = page.locator("[data-testid='location-info']").inner_text().strip()
        except:
            location = "Online / Not specified"

        # PRICE
        try:
            price = page.locator("text=Free").first.inner_text()
        except:
            try:
                price = page.locator("text=₹").first.inner_text()
            except:
                price = "Paid / Unknown"

        # DESCRIPTION (ROBUST)
        description = extract_description(page)

        events_full.append({
            "title": title,
            "datetime": datetime,
            "location": location,
            "mode": infer_mode(location),
            "price": price,
            "is_free": infer_is_free(price),
            "description": description,
            "url": url
        })

        time.sleep(SCROLL_WAIT)  # rate limiting

    browser.close()

# ------------------ SAVE ------------------

df = pd.DataFrame(events_full)

df.to_csv("eventbrite_india_technology_full.csv", index=False)

print("\n✅ DONE")
print("Rows:", len(df))
print("With description:", df["description"].notna().sum())
print(df.head())
