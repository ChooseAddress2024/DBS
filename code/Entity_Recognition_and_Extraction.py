import pandas as pd
import spacy
from fuzzywuzzy import fuzz
import os
import sys

# === Step 1: Load spaCy model ===
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("❌ spaCy model not found. Run: python -m spacy download en_core_web_sm")
    sys.exit(1)

# === Step 2: Load raw CSV input ===
input_file = "D:\\Interview_Prep\\DBS\\data\\financial_crime_news.csv"
if not os.path.exists(input_file):
    print(f"❌ File not found: {input_file}")
    sys.exit(1)

df = pd.read_csv(input_file)

# === Step 3: Perform NER ===
print("🔍 Performing Named Entity Recognition...")

extracted = []

for _, row in df.iterrows():
    content = str(row.get("contents", ""))
    doc = nlp(content)

    people = list(set(ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"))
    orgs = list(set(ent.text.strip() for ent in doc.ents if ent.label_ == "ORG"))

    extracted.append({
        "title": row.get("title", ""),
        "contents": content,
        "published_date": row.get("published_date", ""),
        "people": people,
        "organizations": orgs,
        "url": row.get("url", "")
    })

ner_df = pd.DataFrame(extracted)
ner_output = "D:\\Interview_Prep\\DBS\\data\\extracted_entities_with_text.csv"
ner_df.to_csv(ner_output, index=False)
print(f"✅ NER results saved to: {ner_output}")

# === Step 4: Utility to flatten entity columns safely ===
def safely_flatten_column(col):
    values = []
    for item in col.dropna():
        if isinstance(item, list):
            values.extend(item)
        elif isinstance(item, str):
            try:
                evaluated = eval(item)
                if isinstance(evaluated, list):
                    values.extend(evaluated)
            except:
                continue
    return values

all_people = safely_flatten_column(ner_df["people"])
all_orgs = safely_flatten_column(ner_df["organizations"])

# === Step 5: Group similar entities ===
def group_similar_entities(entities, threshold=85):
    entities = sorted(set(entities))
    groups = []
    seen = set()

    for i, name in enumerate(entities):
        if name in seen:
            continue
        group = [name]
        seen.add(name)
        for j in range(i + 1, len(entities)):
            if entities[j] not in seen and fuzz.token_sort_ratio(name, entities[j]) >= threshold:
                group.append(entities[j])
                seen.add(entities[j])
        groups.append(group)
    
    return groups

def clusters_to_df(clusters, label):
    return pd.DataFrame({
        "cluster_id": [f"{label}_{i+1}" for i in range(len(clusters))],
        "entities": [", ".join(group) for group in clusters],
        "count": [len(group) for group in clusters]
    })

# === Step 6: Cluster people and orgs ===
print("🔁 Grouping similar entities...")

people_clusters = group_similar_entities(all_people)
org_clusters = group_similar_entities(all_orgs)

people_df = clusters_to_df(people_clusters, "PERSON")
orgs_df = clusters_to_df(org_clusters, "ORG")

# === Step 7: Save results ===
people_df.to_csv("D:\\Interview_Prep\\DBS\\data\\disambiguated_people.csv", index=False)
orgs_df.to_csv("D:\\Interview_Prep\\DBS\\data\\disambiguated_organizations.csv", index=False)

print("🎯 Pipeline complete!")
print("📁 Outputs:")
print("   - extracted_entities_with_text.csv")
print("   - disambiguated_people.csv")
print("   - disambiguated_organizations.csv")
