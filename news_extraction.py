import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm
import time

# Settings
start_date = datetime(2020, 1, 8)
end_date = datetime.today()
delta = timedelta(days=1)

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Output storage
news_data = []

print(f"Scraping news from {start_date.date()} to {end_date.date()}...\n")

while start_date <= end_date:
    date_str = start_date.strftime("%Y-%m-%d")
    query_date = start_date.strftime("%m/%d/%Y")
    
    url = f"https://www.bing.com/news/search?q=when:{query_date}&qft=sortbydate"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        headlines = soup.select("a.title")

        if not headlines:
            print(f"No news found for {date_str}")
        for h in headlines:
            title = h.get_text(strip=True)
            news_data.append([date_str, title])
    except Exception as e:
        print(f"Error on {date_str}: {e}")
    
    start_date += delta
    time.sleep(1)  # Avoid getting blocked

# Save to CSV
df = pd.DataFrame(news_data, columns=["Date", "Headline"])
df.to_csv("news_headlines.csv", index=False)
print("\n✅ Headlines saved to 'news_headlines.csv'")
