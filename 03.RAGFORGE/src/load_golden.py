"""
Loads and validates the golden Q&A set against the actual corpus files,
so a typo in a doc filename fails loudly now instead of silently scoring
zero relevant docs later during evaluation.
"""
import json
import os


def load_golden_qa(corpus_dir="corpus", golden_path="data/golden_qa.json"):
    base = os.path.dirname(__file__)
    corpus_dir = os.path.join(base, "..", corpus_dir)
    golden_path = os.path.join(base, "..", golden_path)

    with open(golden_path, "r", encoding="utf-8") as f:
        golden = json.load(f)

    existing_files = set(os.listdir(corpus_dir))

    errors = []
    for entry in golden:
        for doc_id in entry["relevant_docs"]:
            if doc_id not in existing_files:
                errors.append(f"{entry['id']}: '{doc_id}' not found in corpus/")

    if errors:
        raise ValueError("Golden set references missing docs:\n" + "\n".join(errors))

    return golden


def main():
    golden = load_golden_qa()
    print(f"✅ Loaded and validated {len(golden)} golden Q&A pairs")
    for entry in golden:
        print(f"  {entry['id']}: {entry['question'][:60]}... -> {entry['relevant_docs']}")


if __name__ == "__main__":
    main()