import pandas as pd
from fuzzywuzzy import fuzz
from collections import defaultdict

# === Load extracted entities from script 1 ===
df = pd.read_csv("D:\\Interview_Prep\\DBS\\extracted_entities_with_text.csv")

# === Utility function to group similar names ===
def group_similar_entities(entities_list, threshold=85):
    groups = []
    seen = set()

    for i, name in enumerate(entities_list):
        if name in seen:
            continue
        group = [name]
        seen.add(name)
        for j in range(i + 1, len(entities_list)):
            if entities_list[j] not in seen and fuzz.token_sort_ratio(name, entities_list[j]) >= threshold:
                group.append(entities_list[j])
                seen.add(entities_list[j])
        groups.append(group)
    return groups

# === Flatten all person/org entries across rows ===
all_people = [p for sublist in df["people"].dropna().apply(eval) for p in sublist]
all_orgs = [o for sublist in df["organizations"].dropna().apply(eval) for o in sublist]

# === Deduplicate and group ===
unique_people = sorted(set(all_people))
unique_orgs = sorted(set(all_orgs))

people_clusters = group_similar_entities(unique_people)
org_clusters = group_similar_entities(unique_orgs)

# === Save grouped entities ===
def cluster_to_df(clusters, label):
    return pd.DataFrame({
        "cluster_id": [f"{label}_{i+1}" for i in range(len(clusters))],
        "entities": [", ".join(group) for group in clusters],
        "count": [len(group) for group in clusters]
    })

people_df = cluster_to_df(people_clusters, "PERSON")
orgs_df = cluster_to_df(org_clusters, "ORG")

# === Export results ===
people_df.to_csv("D:\\Interview_Prep\\DBS\\disambiguated_people.csv", index=False)
orgs_df.to_csv("D:\\Interview_Prep\\DBS\\disambiguated_organizations.csv", index=False)

print("✅ Entity disambiguation complete.")
print("📄 Saved:")
print("   - disambiguated_people.csv")
print("   - disambiguated_organizations.csv")
