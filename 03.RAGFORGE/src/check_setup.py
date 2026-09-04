from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
import numpy as np
import sklearn
import rich

print("✅ sentence-transformers OK")
print("✅ rank-bm25 OK")
print("✅ numpy OK:", np.__version__)
print("✅ scikit-learn OK:", sklearn.__version__)
print("✅ rich OK")

# Quick smoke test — load a small embedding model to confirm downloads work
model = SentenceTransformer("all-MiniLM-L6-v2")
vec = model.encode("hello world")
print("✅ embedding model loaded, vector shape:", vec.shape)

