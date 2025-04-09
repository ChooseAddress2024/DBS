import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import classification_report
import numpy as np

# Load data
df = pd.read_csv("D:\\Interview_Prep\\DBS\\data\\financial_crime_news.csv")
df["text"] = df["title"].fillna("") + " " + df["contents"].fillna("")

# Define keyword-based rules
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

# Apply weak labeling
def classify_article(text):
    detected = []
    lowered = text.lower()
    for category, keywords in category_keywords.items():
        if any(re.search(r'\b' + re.escape(kw) + r'\b', lowered) for kw in keywords):
            detected.append(category)
    return detected if detected else ["None"]

df["weak_labels"] = df["text"].apply(classify_article)

# Binarize labels
mlb = MultiLabelBinarizer()
y = mlb.fit_transform(df["weak_labels"])

# Vectorize text
vectorizer = TfidfVectorizer(max_features=5000)
X_vec = vectorizer.fit_transform(df["text"])

# Split data
train_idx, test_idx = train_test_split(df.index, test_size=0.2, random_state=42)
X_train, X_test = X_vec[train_idx], X_vec[test_idx]
y_train, y_test = y[train_idx], y[test_idx]

# Train classifier
models = [LogisticRegression(max_iter=1000).fit(X_train, y_train[:, i]) for i in range(y.shape[1])]

# Predict
y_pred = np.array([model.predict(X_test) for model in models]).T
print(classification_report(y_test, y_pred, target_names=mlb.classes_))

# Assign predictions and confidence scores
y_proba_full = np.array([model.predict_proba(X_vec)[:, 1] for model in models]).T
df["rule_based_prediction"] = mlb.inverse_transform(np.array([model.predict(X_vec) for model in models]).T)
df["rule_based_confidence"] = y_proba_full.max(axis=1)

# Save results
df.to_csv("D:\\Interview_Prep\\DBS\\data\\rule_based_classification_results.csv", index=False)
print("Results saved to rule_based_classification_results.csv")