"""
Hybrid retriever: BM25 + Dense fusion (RRF) -> MMR diversity selection ->
Cross-encoder reranking. This is the full pipeline RAGForge will later
generalize into a configurable stage graph.
"""
import numpy as np
from sentence_transformers import CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity

from corpus_loader import load_corpus
from retriever_bm25 import BM25Retriever
from retriever_dense import DenseRetriever


def reciprocal_rank_fusion(rank_lists, k_rrf=60):
    """
    rank_lists: list of ranked doc_id lists (best first), one per retriever.
    Returns doc_ids sorted by fused RRF score (best first).
    """
    scores = {}
    for rank_list in rank_lists:
        for rank, doc_id in enumerate(rank_list):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k_rrf + rank + 1)
    return sorted(scores, key=lambda d: scores[d], reverse=True)


def mmr_select(query_vec, candidate_ids, candidate_vecs, k=5, lam=0.5):
    """
    Greedy MMR selection. lam=1 -> pure relevance, lam=0 -> pure diversity.
    """
    candidate_vecs = np.array(candidate_vecs)
    query_sims = cosine_similarity([query_vec], candidate_vecs)[0]

    selected = []
    remaining = list(range(len(candidate_ids)))

    while remaining and len(selected) < k:
        if not selected:
            best = max(remaining, key=lambda i: query_sims[i])
        else:
            def mmr_score(i):
                relevance = query_sims[i]
                diversity = max(
                    cosine_similarity([candidate_vecs[i]], [candidate_vecs[j]])[0][0]
                    for j in selected
                )
                return lam * relevance - (1 - lam) * diversity
            best = max(remaining, key=mmr_score)

        selected.append(best)
        remaining.remove(best)

    return [candidate_ids[i] for i in selected]


class HybridRetriever:
    def __init__(self, corpus_dir="corpus", cross_encoder_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.doc_ids, self.texts = load_corpus(corpus_dir)
        self.id_to_text = dict(zip(self.doc_ids, self.texts))

        self.bm25 = BM25Retriever(corpus_dir)
        self.dense = DenseRetriever(corpus_dir)
        self.cross_encoder = CrossEncoder(cross_encoder_name)

        # Cache dense embeddings for MMR (reuse dense retriever's)
        self.id_to_vec = dict(zip(self.dense.doc_ids, self.dense.doc_embeddings))

    def retrieve(self, query, k=5, fusion_pool=15, mmr_pool=10, lam=0.5):
        # Stage 1: get ranked candidates from both retrievers (wide pool)
        bm25_results = self.bm25.retrieve(query, k=fusion_pool)
        dense_results = self.dense.retrieve(query, k=fusion_pool)

        bm25_ids = [d for d, _ in bm25_results]
        dense_ids = [d for d, _ in dense_results]

        # Stage 2: fuse rankings with RRF
        fused_ids = reciprocal_rank_fusion([bm25_ids, dense_ids])[:fusion_pool]

        # Stage 3: MMR diversity selection over the fused shortlist
        query_vec = self.dense.model.encode([query], convert_to_numpy=True)[0]
        candidate_vecs = [self.id_to_vec[d] for d in fused_ids]
        mmr_ids = mmr_select(query_vec, fused_ids, candidate_vecs, k=mmr_pool, lam=lam)

        # Stage 4: cross-encoder reranking on the MMR-selected set
        pairs = [(query, self.id_to_text[d]) for d in mmr_ids]
        rerank_scores = self.cross_encoder.predict(pairs, show_progress_bar=False)
        reranked = sorted(zip(mmr_ids, rerank_scores), key=lambda x: x[1], reverse=True)
        return [(doc_id, float(score)) for doc_id, score in reranked[:k]]


if __name__ == "__main__":
    retriever = HybridRetriever()
    query = "What does HNSW stand for and how does it work?"
    results = retriever.retrieve(query, k=5)
    print(f"Query: {query}\n")
    for doc_id, score in results:
        print(f"  {score:.3f}  {doc_id}")
