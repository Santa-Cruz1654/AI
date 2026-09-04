# Hybrid Search Benchmark

A rehearsal mini-project for [RAGForge](../)'s retrieval layer: compares
dense-only, BM25-only, and hybrid (dense + BM25 fusion + MMR + cross-encoder
reranking) retrieval on a small hand-curated corpus and golden Q&A set.

## Setup

Corpus: 18 short original documents on cloud/AI security topics (`corpus/`),
deliberately written with topic overlap (e.g. separate docs on BM25, dense
embeddings, and hybrid search) so the three retrieval strategies produce
genuinely different rankings instead of trivially agreeing.

Golden set: 15 hand-written Q&A pairs (`data/golden_qa.json`), covering:
- exact keyword/acronym queries (should favor BM25)
- paraphrased/semantic queries with low vocabulary overlap (should favor dense)
- queries with 2 valid relevant docs (tests precision under ambiguity)
- general conceptual queries with plausible distractors

## Configs compared

| Config | Pipeline |
|---|---|
| BM25-only | Lexical term matching (rank_bm25, k1/b defaults) |
| Dense-only | Bi-encoder embeddings (`all-MiniLM-L6-v2`) + cosine similarity |
| Hybrid+MMR+Rerank | BM25 + Dense candidates → Reciprocal Rank Fusion → MMR diversity selection → cross-encoder rerank (`cross-encoder/ms-marco-MiniLM-L-6-v2`) |

## Results

**Precision@5 / Recall@5** (k=5, 18-doc corpus):

| Config | Mean P@5 | Mean R@5 |
|---|---|---|
| BM25-only | 0.227 | 1.000 |
| Dense-only | 0.227 | 1.000 |
| Hybrid+MMR+Rerank | 0.227 | 1.000 |

These are identical across all three configs — **not a bug** (verified: 0/15
queries returned identical top-5 document sets across configs — see
`src/diagnose_ties.py`). On an 18-document corpus with mostly 1 relevant doc
per query, retrieving 5 candidates makes recall@5=1.0 easy to hit for any
reasonable retriever, and precision@5 saturates around the same value once
the one correct doc is *somewhere* in the top 5. At this corpus size, P@5/R@5
don't discriminate between retrieval quality — they only confirm all three
configs are "good enough" to not miss the answer entirely.

**Precision@1 / MRR** (the metrics that actually separate the configs):

| Config | P@1 | MRR |
|---|---|---|
| BM25-only | 0.800 | 0.889 |
| Dense-only | 0.933 | 0.967 |
| Hybrid+MMR+Rerank | **1.000** | **1.000** |

## Winner: Hybrid + MMR + Cross-Encoder Rerank

Hybrid placed the correct document at **rank 1 for all 15 queries** — the
only config to do so. The gap between configs shows up specifically in
**ranking precision**, not coverage:

- **BM25 failed hardest on paraphrased queries** — e.g. "What does HNSW
  stand for and how does it work?" ranked `doc03_bm25_ranking.txt` (an
  unrelated doc *about* BM25) above the actually-correct `doc13` at #2,
  because "does," "how," "work" are common tokens shared with doc03's
  phrasing. Pure lexical matching has no notion that doc13 is topically
  closer.
- **Dense mostly fixed that** but still occasionally misranked on queries
  where two docs are semantically close (e.g. the lexical-vs-semantic
  retrieval question, where dense scored `doc05_hybrid_search.txt` above
  one of the two truly relevant docs).
- **Hybrid's cross-encoder reranking stage resolved the remaining
  ambiguity** — by jointly encoding query and candidate rather than
  comparing precomputed vectors, it distinguishes fine-grained relevance
  that cosine similarity alone misses, at the cost of extra latency (it
  only reranks a small shortlist, not the full corpus, to keep this
  affordable).

**Practical takeaway for RAGForge:** on small-to-medium corpora, retrieval
*coverage* (recall@k) is rarely the differentiator — most reasonable
retrievers will surface the right document somewhere in a top-5. The real
value of hybrid + reranking is **ranking precision**: getting the correct
document to rank #1 reliably, which matters a lot when only the top 1-2
retrieved chunks are passed to an LLM (as is typical in production RAG to
control context/cost), rather than the top 5.

## Reproducing

```bash
uv run src/build_corpus.py
uv run src/load_golden.py
uv run src/evaluate.py
uv run src/compute_extra_metrics.py
```

Full per-query results: `results/eval_results.json`