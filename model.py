import os
import pandas as pd
from datetime import timedelta
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm

df = pd.read_csv("tesla_crash_headlines.csv", parse_dates=["news_date"])


model = SentenceTransformer("all-MiniLM-L6-v2")

df["news_date"] = pd.to_datetime(df["news_date"])
df = df.sort_values("news_date")


df["week_start"] = df["news_date"].apply(lambda x: x - timedelta(days=x.weekday()))


checkpoint_file = "processed_weeks.txt"
output_file = "repeating_headlines_3plus.csv"

if os.path.exists(checkpoint_file):
    with open(checkpoint_file, "r") as f:
        processed_weeks = set(pd.to_datetime(line.strip()) for line in f)
else:
    processed_weeks = set()

if os.path.exists(output_file):
    output_df = pd.read_csv(output_file)
else:
    output_df = pd.DataFrame(columns=["week_start", "news_date", "headline", "repeat_count"])

seen_headlines = set()  
for week_start in tqdm(df["week_start"].unique(), desc="Processing weeks"):
    if week_start in processed_weeks:
        continue  

    week_end = week_start + timedelta(days=6)
    week_df = df[(df["news_date"] >= week_start) & (df["news_date"] <= week_end)].copy()
    other_df = df[(df["news_date"] < week_start) | (df["news_date"] > week_end)].copy()

    for row in week_df.itertuples():
        if row.headline in seen_headlines:
            continue

        count = 0
        headline_embedding = model.encode(row.headline, convert_to_tensor=True)
        matched_headlines = []

        for other_row in other_df.itertuples():
            if other_row.headline in seen_headlines:
                continue
            similarity = float(util.cos_sim(headline_embedding, model.encode(other_row.headline, convert_to_tensor=True))[0])
            if similarity >= 0.8:
                count += 1
                matched_headlines.append(other_row.headline)

        if count >= 3:
            output_df.loc[len(output_df)] = {
                "week_start": week_start,
                "news_date": row.news_date,
                "headline": row.headline,
                "repeat_count": count
            }
            seen_headlines.add(row.headline)
            for match in matched_headlines:
                seen_headlines.add(match)

    output_df.to_csv(output_file, index=False)
    with open(checkpoint_file, "a") as f:
        f.write(str(week_start.date()) + "\n")

print("✅ Done! Checkpoints saved. You can resume if interrupted.")
