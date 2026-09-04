"""
Computes precision@1 and Mean Reciprocal Rank (MRR) from the already-saved
eval_results.json, without re-running any retriever. These metrics are more
discriminating than P@5/R@5 on a small corpus where recall@5 saturates to 1.0.
"""
import json
import os

path = os.path.join(os.path.dirname(__file__), "..", "results", "eval_results.json")
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

details = data["details"]

print(f"{'Config':<20} {'P@1':>8} {'MRR':>8}")
print("-" * 38)

extra_summary = []
for config_name, queries in details.items():
    hits_at_1 = 0
    reciprocal_ranks = []

    for q in queries:
        relevant = set(q["relevant_docs"])
        retrieved = q["retrieved_docs"]

        if retrieved and retrieved[0] in relevant:
            hits_at_1 += 1

        rr = 0.0
        for rank, doc_id in enumerate(retrieved, start=1):
            if doc_id in relevant:
                rr = 1.0 / rank
                break
        reciprocal_ranks.append(rr)

    n = len(queries)
    p_at_1 = hits_at_1 / n
    mrr = sum(reciprocal_ranks) / n

    print(f"{config_name:<20} {p_at_1:>8.3f} {mrr:>8.3f}")
    extra_summary.append({"config": config_name, "precision_at_1": round(p_at_1, 3), "mrr": round(mrr, 3)})

# Merge into eval_results.json
data["extra_metrics"] = extra_summary
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"\nSaved extra_metrics into {path}")