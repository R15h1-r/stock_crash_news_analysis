import pandas as pd
import yfinance as yf
from datetime import timedelta

# Step 1: Download Tesla stock data
ticker = 'TSLA'
stock_data = yf.download(ticker, start="2020-01-01", end="2025-06-25")
stock_data['Drop %'] = stock_data['Close'].pct_change() * 100

# Step 2: Identify crash dates (drop >= 5%)
crash_days = stock_data[stock_data['Drop %'] <= -5].index

# Step 3: Load news headlines
news_df = pd.read_csv("news_headlines1.csv", parse_dates=['Date'])

# Step 4: Extract headlines 6 days before and on the day of crash
crash_headlines = []

for crash_date in crash_days:
    start_date = crash_date - timedelta(days=6)
    mask = (news_df['Date'] >= start_date) & (news_df['Date'] <= crash_date)
    crash_week_headlines = news_df[mask]

    for _, row in crash_week_headlines.iterrows():
        crash_headlines.append({
            'crash_date': crash_date.date(),
            'news_date': row['Date'].date(),
            'headline': row['Headline']
        })

crash_headlines_df = pd.DataFrame(crash_headlines)
crash_headlines_df.to_csv("tesla_crash_headlines.csv", index=False)
print("✅ Saved to 'tesla_crash_headlines.csv'")