import pandas as pd
import spacy
import os
import sys

# === Step 1: Check NumPy import health ===
try:
    import numpy
    _ = numpy.__version__  # Force use to confirm it's valid
except Exception as e:
    print("\n❌ NumPy is broken or improperly installed.")
    print("📌 Run the following in your terminal/Anaconda Prompt:")
    print("   pip uninstall numpy")
    print("   pip install numpy --upgrade --force-reinstall")
    sys.exit(1)

# === Step 2: Load spaCy model with guidance if missing ===
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("\n❌ spaCy model 'en_core_web_sm' not found.")
    print("📌 Run the following to install it:")
    print("   python -m spacy download en_core_web_sm")
    sys.exit(1)

# === Step 3: Load your CSV ===
csv_path = "financial_crime_news_last_day.csv"  # <-- Modify this if needed
if not os.path.exists(csv_path):
    print(f"\n❌ CSV file not found at: {csv_path}")
    sys.exit(1)

df = pd.read_csv(csv_path)

# === Step 4: Perform NER on each article ===
results = []

for _, row in df.iterrows():
    content = str(row.get("contents", ""))
    doc = nlp(content)

    people = list(set(ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"))
    orgs = list(set(ent.text.strip() for ent in doc.ents if ent.label_ == "ORG"))

    results.append({
        "title": row.get("title", ""),
        "contents": content,
        "published_date": row.get("published_date", ""),
        "people": people,
        "organizations": orgs,
        "url": row.get("url", "")
    })

# === Step 5: Save results ===
output_path = "D:\\Interview_Prep\\DBS\\data\\extracted_entities_with_text.csv"
entities_df = pd.DataFrame(results)
entities_df.to_csv(output_path, index=False)

print(f"\n✅ Named entities extracted and saved to: {output_path}")
