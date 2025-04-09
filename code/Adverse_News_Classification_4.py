import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Load your data
# Load data with comprehensive null handling
df = pd.read_csv("d:\\Interview_Prep\\DBS\\data\\financial_crime_news.csv")

# Enhanced text processing with debug checks
print("Original data shape:", df.shape)
print("Null values in title:", df["title"].isna().sum())
print("Null values in contents:", df["contents"].isna().sum())

# Safe text processing with multiple fallbacks
df["text"] = df.apply(lambda row: 
                     (str(row["title"]) if pd.notna(row["title"]) else "") + " " + 
                     (str(row["contents"]) if pd.notna(row["contents"]) else ""), 
                     axis=1)

# Debug checks
print("After processing - Null values:", df["text"].isna().sum())
print("After processing - Empty strings:", df["text"].str.strip().eq('').sum())

# Remove problematic entries
df = df[~df["text"].isna() & (df["text"].str.strip() != "")]
print("Final data shape:", df.shape)

# Additional validation
if df.empty:
    raise ValueError("No valid text data remaining after preprocessing")

# Generate embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(df["text"].tolist(), show_progress_bar=True)

# KMeans clustering with full initialization
# Set environment variables before importing sklearn
import os
os.environ['OMP_NUM_THREADS'] = '1'  # Limit OpenMP threads
os.environ['MKL_NUM_THREADS'] = '1'  # Limit MKL threads

# KMeans clustering with full error handling
try:
    kmeans = KMeans(n_clusters=5, 
                   random_state=42, 
                   n_init=10,  # Explicit n_init instead of 'auto'
                   init='k-means++')
    kmeans.fit(embeddings)
except Exception as e:
    print(f"Clustering failed: {str(e)}")
    # Fallback: assign all to cluster 0 with low confidence
    df["embedding_cluster"] = 0
    df["embedding_confidence"] = 0.5
    df.to_csv("D:\\Interview_Prep\\DBS\\data\\embedding_clustering_results.csv", index=False)
    raise SystemExit("Failed to perform clustering - saved fallback results")

# Verify model is fitted
if not hasattr(kmeans, 'cluster_centers_'):
    raise RuntimeError("KMeans failed to initialize properly")

# Assign clusters and compute confidence
df["embedding_cluster"] = kmeans.labels_
centroids = kmeans.cluster_centers_  # Now safe to access
df["embedding_confidence"] = cosine_similarity(embeddings, centroids).max(axis=1)

# Save or preview
df.to_csv("D:\\Interview_Prep\\DBS\\data\\embedding_clustering_results.csv", index=False)
print(df[["title", "embedding_category", "embedding_confidence"]].head())
