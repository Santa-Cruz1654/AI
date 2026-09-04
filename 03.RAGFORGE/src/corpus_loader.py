"""
Loads all corpus documents into memory as (doc_id, text) pairs.
Since our docs are already small (one topic each), we treat each whole
file as a single chunk — no splitting needed for this mini-project.
"""
import os


def load_corpus(corpus_dir="corpus"):
    base = os.path.dirname(__file__)
    corpus_dir = os.path.join(base, "..", corpus_dir)

    doc_ids = []
    texts = []
    for filename in sorted(os.listdir(corpus_dir)):
        if not filename.endswith(".txt"):
            continue
        path = os.path.join(corpus_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            texts.append(f.read())
        doc_ids.append(filename)

    return doc_ids, texts


if __name__ == "__main__":
    doc_ids, texts = load_corpus()
    print(f"✅ Loaded {len(doc_ids)} docs")
    print(f"First doc: {doc_ids[0]} ({len(texts[0])} chars)")