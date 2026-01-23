from playwright.sync_api import sync_playwright
import pandas as pd
import time

df = pd.read_csv("eventbrite_india_technology_events.csv")

details = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for i, row in df.iterrows():
        url = row["url"]
        print(f"[{i+1}/{len(df)}] {url}")

        try:
            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )
        except:
            print("Skipping (timeout)")
            continue

        time.sleep(2)

        # ---- TITLE ----
        try:
            title = page.locator("h1").first.inner_text()
        except:
            title = row["title"]

        # ---- DATE & TIME ----
        try:
            datetime = page.locator("time").first.inner_text()
        except:
            datetime = None

        # ---- LOCATION ----
        try:
            location = page.locator(
                "[data-testid='location-info']"
            ).inner_text()
        except:
            location = "Online / Not specified"

        # ---- PRICE (FREE / PAID) ----
        try:
            price = page.locator(
                "text=Free"
            ).first.inner_text()
        except:
            try:
                price = page.locator(
                    "text=₹"
                ).first.inner_text()
            except:
                price = "Paid / Unknown"

        # ---- DESCRIPTION ----
        try:
            desc = page.locator(
                "[data-testid='structured-description']"
            ).inner_text()
        except:
            desc = None

        details.append({
            "title": title,
            "datetime": datetime,
            "location": location,
            "price": price,
            "description": desc,
            "url": url
        })

        time.sleep(2)  # RATE LIMIT

    browser.close()

out = pd.DataFrame(details)
out.to_csv("eventbrite_india_tech_full.csv", index=False)

print("\n✅ Detailed events saved")
