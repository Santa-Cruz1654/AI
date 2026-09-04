"""
Compares retrieved doc lists across configs for each query to check
whether the tied precision/recall numbers reflect genuinely different
(but equally-scoring) retrievals, or a bug where configs return identical
lists.
"""
import json
import os

path = os.path.join(os.path.dirname(__file__), "..", "results", "eval_results.json")
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

details = data["details"]
configs = list(details.keys())
n_queries = len(details[configs[0]])

identical_count = 0
for i in range(n_queries):
    entries = [details[c][i] for c in configs]
    qid = entries[0]["id"]
    lists = [tuple(e["retrieved_docs"]) for e in entries]
    all_same = len(set(lists)) == 1
    if all_same:
        identical_count += 1
    print(f"{qid}: identical={all_same}")
    for c, e in zip(configs, entries):
        print(f"    {c:20s} {e['retrieved_docs']}")

print(f"\n{identical_count}/{n_queries} queries had identical top-5 lists across all 3 configs")