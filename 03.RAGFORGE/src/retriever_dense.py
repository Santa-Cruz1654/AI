"""
Dense-only retriever using a bi-encoder (all-MiniLM-L6-v2) and cosine
similarity. Embeddings are computed once at init and cached in memory.
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from corpus_loader import load_corpus


class DenseRetriever:
    def __init__(self, corpus_dir="corpus", model_name="all-MiniLM-L6-v2"):
        self.doc_ids, self.texts = load_corpus(corpus_dir)
        self.model = SentenceTransformer(model_name)
        self.doc_embeddings = self.model.encode(
            self.texts, convert_to_numpy=True, show_progress_bar=False
        )

    def retrieve(self, query, k=5):
        query_vec = self.model.encode([query], convert_to_numpy=True)
        sims = cosine_similarity(query_vec, self.doc_embeddings)[0]
        ranked = np.argsort(sims)[::-1][:k]
        return [(self.doc_ids[i], float(sims[i])) for i in ranked]


if __name__ == "__main__":
    retriever = DenseRetriever()
    query = "What does HNSW stand for and how does it work?"
    results = retriever.retrieve(query, k=5)
    print(f"Query: {query}\n")
    for doc_id, score in results:
        print(f"  {score:.3f}  {doc_id}")