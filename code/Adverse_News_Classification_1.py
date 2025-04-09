import re
import pandas as pd

input_file = "D:\\Interview_Prep\\DBS\\data\\financial_crime_news.csv"
df = pd.read_csv(input_file)

# Define simulated category patterns for zero-shot classification
category_keywords = {
    "Money Laundering": ["money laundering", "laundered funds", "illicit finance", "shell company"],
    "Terrorist Financing": ["terrorist financing", "terror funding", "extremist funding"],
    "Sanctions Violations": ["sanctions violation", "bypassing sanctions", "blocked entity"],
    "Fraud": ["fraud", "scam", "deceptive", "forgery", "fake"],
    "Tax Evasion": ["tax evasion", "underreporting", "offshore tax", "avoid taxes"],
    "Bribery and Corruption": ["bribe", "kickback", "corruption", "graft"],
    "Insider Trading": ["insider trading", "non-public information", "market manipulation"],
    "Ponzi and Pyramid Schemes": ["ponzi scheme", "pyramid scheme", "investment scam"],
    "Trade-Based Money Laundering": ["trade-based money laundering", "over-invoicing", "misinvoicing"]
}

# Combine title and content
df["text"] = df["title"].fillna("") + " " + df["contents"].fillna("")

# Simulate zero-shot classification
def classify_article(text):
    detected = []
    lowered = text.lower()
    for category, keywords in category_keywords.items():
        if any(re.search(r'\b' + re.escape(kw) + r'\b', lowered) for kw in keywords):
            detected.append(category)
    return detected if detected else ["None"]

df["zero_shot_prediction"] = df["text"].apply(classify_article)

# Assign a simulated confidence score (based on number of matched keywords)
def confidence_score(text, matched_categories):
    if "None" in matched_categories:
        return 0.1
    score = 0
    lowered = text.lower()
    for category in matched_categories:
        if category == "None":
            continue
        keywords = category_keywords.get(category, [])
        matches = sum(1 for kw in keywords if kw in lowered)
        score += matches
    return min(round(score / 5, 2), 1.0)  # Normalize score between 0 and 1

df["zero_shot_confidence"] = df.apply(
    lambda row: confidence_score(row["text"], row["zero_shot_prediction"]),
    axis=1
)

df.to_csv("D:\\Interview_Prep\\DBS\\data\\zero_shot_prediction.csv", index=False)

