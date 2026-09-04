"""
BM25-only sparse retriever. Pure lexical matching — tokenizes on
whitespace + lowercasing, no stemming, to keep it simple and transparent.
"""
import re
from rank_bm25 import BM25Okapi
from corpus_loader import load_corpus


def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


class BM25Retriever:
    def __init__(self, corpus_dir="corpus"):
        self.doc_ids, self.texts = load_corpus(corpus_dir)
        tokenized_corpus = [tokenize(t) for t in self.texts]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def retrieve(self, query, k=5):
        tokenized_query = tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        ranked = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )[:k]
        return [(self.doc_ids[i], float(scores[i])) for i in ranked]


if __name__ == "__main__":
    retriever = BM25Retriever()
    query = "What does HNSW stand for and how does it work?"
    results = retriever.retrieve(query, k=5)
    print(f"Query: {query}\n")
    for doc_id, score in results:
        print(f"  {score:.3f}  {doc_id}")