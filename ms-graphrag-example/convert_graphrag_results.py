import pandas as pd
import json

df = pd.read_csv("ms-graphrag-results/local-search-sources.csv")

results = []
for _, row in df.iterrows():
    results.append({
        "query": row["query"],
        "source": row["text"]
    })

with open("ms-graphrag-results/graphrag_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)