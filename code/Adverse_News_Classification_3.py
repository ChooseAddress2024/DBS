import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier  # or whatever model type you're using
from joblib import load  # or import pickle

df = pd.read_csv("D:\\Interview_Prep\\DBS\\data\\financial_crime_news.csv")

# Option 1: If models are already trained and saved
models = [
    load("D:\\Interview_Prep\\DBS\\models\\model1.joblib"),
    load("D:\\Interview_Prep\\DBS\\models\\model2.joblib")
    # Add more models as needed
]

# Option 2: If you need to train new models
# models = [
#     RandomForestClassifier().fit(X_train, y_train),
#     # Add other trained models here
# ]

# Recompute probability scores
y_proba_full = np.array([model.predict_proba(X_vec)[:, 1] for model in models]).T

# Assign max confidence score for each sample
df["rule_based_confidence"] = y_proba_full.max(axis=1)

# Display final rule-based classification results
tools.display_dataframe_to_user(
    name="Rule-Based Classification Results (Final)",
    dataframe=df.loc[test_idx, ["title", "rule_based_prediction", "rule_based_confidence"]]
)
df.head()