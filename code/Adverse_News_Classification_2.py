# Install required packages
# !pip install bertopic sentence-transformers

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
import pandas as pd

# Load your dataset
df = pd.read_csv("D:\\Interview_Prep\\DBS\\data\\financial_crime_news.csv")
df["text"] = df["title"].fillna("") + " " + df["contents"].fillna("")

# Generate embeddings
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
docs = df["text"].tolist()
embeddings = embedding_model.encode(docs, show_progress_bar=True)

# Fit BERTopic
from transformers import __version__ as transformers_version
from packaging import version

# Fit BERTopic
if version.parse(transformers_version) >= version.parse("4.31.0"):
    topic_model = BERTopic(embedding_model=embedding_model)
else:
    topic_model = BERTopic()
topics, probs = topic_model.fit_transform(docs, embeddings)

# Add to DataFrame
df["bertopic_topic"] = topics
df["bertopic_topic_name"] = df["bertopic_topic"].apply(lambda x: topic_model.get_topic(x)[0] if x != -1 else "Outlier")
df["bertopic_confidence"] = [max(p) if p else 0.0 for p in probs]

# Save or preview
df.to_csv("D:\\Interview_Prep\\DBS\\data\\bertopic_results.csv", index=False)
print(df[["title", "bertopic_topic", "bertopic_topic_name", "bertopic_confidence"]].head())
