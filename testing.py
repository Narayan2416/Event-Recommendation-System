import pandas as pd
import webbrowser

df = pd.read_csv("data/eventbrite_clean_for_recommendation.csv")

urls = df["url"].dropna().tolist()
c=0

batch_size = 10
total = len(urls)

for i in range(c, total, batch_size):
    batch = urls[i:i + batch_size]

    print(f"\nOpening events {i+1} to {i+len(batch)}")

    for url in batch:
        webbrowser.open(url)

    if i + batch_size >= total:
        print("\nNo more links.")
        break

    user_input = input("\nOpen next 10 links? (y/n): ").strip().lower()
    if user_input != "y":
        print("Stopped by user.")
        break
    c+=1
print(c)
