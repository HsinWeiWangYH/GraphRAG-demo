import json
import pandas as pd

df = pd.read_csv("../lightrag-results/lightrag-local-search-chunks.csv")

results = []
for _, row in df.iterrows():
    results.append({
        "query": row["query"],
        "source": row["content"]
    })

with open("../lightrag-results/graphrag_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)