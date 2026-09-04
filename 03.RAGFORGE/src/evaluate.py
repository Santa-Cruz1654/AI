"""
Runs all three retrieval configs (BM25, Dense, Hybrid) against the golden
Q&A set and computes precision@k / recall@k per config, plus a summary
table. Results are also saved to results/eval_results.json.
"""
import json
import os
from rich.console import Console
from rich.table import Table

from load_golden import load_golden_qa
from retriever_bm25 import BM25Retriever
from retriever_dense import DenseRetriever
from retriever_hybrid import HybridRetriever

K = 5  # top-k cutoff for all metrics
console = Console()


def precision_recall_at_k(retrieved_ids, relevant_ids, k):
    retrieved_top_k = retrieved_ids[:k]
    relevant_set = set(relevant_ids)

    hits = [doc_id for doc_id in retrieved_top_k if doc_id in relevant_set]
    precision = len(hits) / k if k > 0 else 0.0
    recall = len(hits) / len(relevant_set) if relevant_set else 0.0
    return precision, recall


def evaluate_config(name, retriever, golden, k=K):
    per_query = []
    total_p, total_r = 0.0, 0.0

    for entry in golden:
        results = retriever.retrieve(entry["question"], k=k)
        retrieved_ids = [doc_id for doc_id, _ in results]
        p, r = precision_recall_at_k(retrieved_ids, entry["relevant_docs"], k)

        total_p += p
        total_r += r
        per_query.append({
            "id": entry["id"],
            "question": entry["question"],
            "relevant_docs": entry["relevant_docs"],
            "retrieved_docs": retrieved_ids,
            "precision_at_k": round(p, 3),
            "recall_at_k": round(r, 3),
        })

    n = len(golden)
    summary = {
        "config": name,
        "k": k,
        "mean_precision_at_k": round(total_p / n, 3),
        "mean_recall_at_k": round(total_r / n, 3),
    }
    return summary, per_query


def main():
    golden = load_golden_qa()
    console.print(f"[bold]Loaded {len(golden)} golden Q&A pairs, k={K}[/bold]\n")

    configs = [
        ("BM25-only", BM25Retriever()),
        ("Dense-only", DenseRetriever()),
        ("Hybrid+MMR+Rerank", HybridRetriever()),
    ]

    all_summaries = []
    all_details = {}

    for name, retriever in configs:
        console.print(f"[cyan]Running {name}...[/cyan]")
        summary, per_query = evaluate_config(name, retriever, golden)
        all_summaries.append(summary)
        all_details[name] = per_query

    # --- Print summary table ---
    table = Table(title=f"Retrieval Config Comparison (k={K})")
    table.add_column("Config", style="bold")
    table.add_column("Mean Precision@k", justify="right")
    table.add_column("Mean Recall@k", justify="right")

    for s in all_summaries:
        table.add_row(s["config"], f"{s['mean_precision_at_k']:.3f}", f"{s['mean_recall_at_k']:.3f}")

    console.print("\n")
    console.print(table)

    # --- Identify winner ---
    winner = max(all_summaries, key=lambda s: (s["mean_precision_at_k"] + s["mean_recall_at_k"]))
    console.print(f"\n[bold green]Winner (by P+R): {winner['config']}[/bold green]")

    # --- Save full results to disk ---
    out_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "eval_results.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"summary": all_summaries, "details": all_details}, f, indent=2)

    console.print(f"\n[dim]Full per-query results saved to {out_path}[/dim]")


if __name__ == "__main__":
    main()