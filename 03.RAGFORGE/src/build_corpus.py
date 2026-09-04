"""
Generates a small, fixed corpus of 18 short documents on cloud/AI security
topics. Each doc is deliberately scoped to 1-2 concepts so retrieval configs
can be meaningfully compared (i.e. some docs are near-duplicates in topic,
which is what makes BM25 vs dense vs hybrid actually diverge).
"""
import os

CORPUS = {
    "doc01_iam_least_privilege.txt": """Least Privilege in IAM
The principle of least privilege means granting a user, service, or process
only the permissions strictly necessary to perform its function, nothing
more. In cloud IAM systems, this typically means avoiding wildcard
permissions like Action:* or Resource:*, and instead scoping policies to
specific actions on specific resources. Over-permissioned roles are one of
the most common root causes of cloud breaches, since a single compromised
credential can then be used to pivot across an entire account.""",

    "doc02_iam_role_assumption.txt": """Role Assumption and Temporary Credentials
Cloud providers allow identities to assume roles, receiving short-lived
temporary credentials instead of long-lived access keys. This reduces the
blast radius of credential leakage because assumed-role sessions expire
automatically, often within an hour. Role assumption is also the basis for
cross-account access patterns, where a trusted account is granted permission
to assume a role in another account without sharing static secrets.""",

    "doc03_bm25_ranking.txt": """BM25 Ranking Function
BM25 is a bag-of-words ranking function used by search engines to estimate
the relevance of documents to a query. It builds on TF-IDF by adding term
frequency saturation and document length normalization, controlled by
parameters k1 and b. BM25 is purely lexical: it matches exact tokens and
does not understand synonyms or semantic similarity, which is why queries
using different wording than the source document can fail to retrieve it.""",

    "doc04_dense_embeddings.txt": """Dense Retrieval with Embeddings
Dense retrieval encodes both queries and documents into fixed-length vectors
using a neural encoder, then ranks documents by vector similarity (usually
cosine similarity). Unlike BM25, dense retrieval captures semantic meaning,
so a query can match a relevant passage even if it shares no exact words
with it. The tradeoff is that dense retrieval can sometimes miss exact
keyword matches, such as specific error codes, product names, or IDs.""",

    "doc05_hybrid_search.txt": """Hybrid Search
Hybrid search combines lexical retrieval (like BM25) with dense vector
retrieval, merging their result sets to get both exact keyword matching and
semantic understanding. A common approach is Reciprocal Rank Fusion (RRF),
which combines rankings from multiple retrievers without needing to
normalize their raw scores. Hybrid search generally outperforms either
method alone on real-world query sets, which mix specific terms and vague
natural-language phrasing.""",

    "doc06_mmr_diversity.txt": """Maximal Marginal Relevance (MMR)
MMR is a re-ranking technique that balances relevance to the query against
redundancy among the selected results. It iteratively picks the next
document that maximizes relevance minus similarity to already-selected
documents, controlled by a lambda parameter. MMR is used to avoid returning
five near-duplicate chunks from the same section of a document, improving
the diversity of context passed to a downstream LLM.""",

    "doc07_cross_encoder_reranking.txt": """Cross-Encoder Reranking
A cross-encoder jointly encodes a query and a candidate document in a single
forward pass, allowing it to model fine-grained interactions between them.
This makes cross-encoders far more accurate than bi-encoder dense retrieval
for relevance judgment, but also much slower, since every query-document
pair must be scored individually. In practice, cross-encoders are used to
rerank a small shortlist (e.g. top 20-50) retrieved cheaply by a bi-encoder
or BM25 first.""",

    "doc08_s3_bucket_misconfig.txt": """S3 Bucket Misconfiguration
Publicly accessible storage buckets remain one of the most common cloud
misconfigurations leading to data breaches. Default bucket policies should
deny public access, and organizations should enable account-level Block
Public Access settings as a safety net against accidental exposure. Bucket
policies and ACLs should be audited regularly, since a single overly
permissive policy statement can expose an entire dataset.""",

    "doc09_encryption_at_rest.txt": """Encryption at Rest
Encryption at rest protects stored data by encrypting it on disk, so that
someone with access to the underlying storage medium cannot read the data
without the decryption key. Cloud providers typically offer both
provider-managed keys and customer-managed keys (CMK); using CMKs gives the
customer control over key rotation and revocation, which matters for
compliance requirements like key destruction on data deletion.""",

    "doc10_encryption_in_transit.txt": """Encryption in Transit
Encryption in transit protects data as it moves between systems, typically
via TLS. It prevents on-path attackers from reading or tampering with data
crossing a network, including internal traffic between microservices.
Modern security baselines require TLS 1.2 or higher and disable weak cipher
suites, since older protocol versions have known cryptographic weaknesses
that can be exploited to decrypt traffic.""",

    "doc11_prompt_injection.txt": """Prompt Injection
Prompt injection is an attack where malicious input is crafted to override
or manipulate an LLM's intended instructions, often by embedding hidden
commands inside content the model processes, such as a webpage or document.
Indirect prompt injection is especially dangerous in RAG systems, since
retrieved documents become part of the model's context and can carry
attacker-controlled instructions that the model may follow unless the
system is designed to treat retrieved content as untrusted data.""",

    "doc12_rag_architecture.txt": """RAG Architecture Overview
Retrieval-Augmented Generation combines a retrieval system with a language
model: relevant documents are fetched from a corpus based on the query, then
passed to the LLM as context alongside the question. This grounds the
model's answers in the retrieved evidence and reduces hallucination compared
to relying purely on the model's parametric knowledge. Retrieval quality is
usually the dominant factor in overall RAG system quality.""",

    "doc13_vector_db_indexing.txt": """Vector Database Indexing (HNSW)
Approximate nearest neighbor search in vector databases commonly uses HNSW
(Hierarchical Navigable Small World) graphs, which trade a small amount of
recall for large gains in query speed compared to exact nearest neighbor
search. HNSW builds multiple layers of proximity graphs, allowing search to
start coarse at the top layer and refine at lower layers, making it
practical to query millions of vectors in milliseconds.""",

    "doc14_zero_trust_architecture.txt": """Zero Trust Architecture
Zero trust assumes no implicit trust based on network location; every
request must be authenticated and authorized regardless of whether it
originates inside or outside the traditional network perimeter. This
contrasts with older perimeter-based security models where anything inside
the firewall was implicitly trusted. Zero trust typically relies on strong
identity verification, device posture checks, and fine-grained
policy-based access control for every request.""",

    "doc15_secrets_management.txt": """Secrets Management
Hardcoding credentials, API keys, and tokens directly in source code or
config files is a major source of credential leaks, especially when code is
pushed to public repositories. Dedicated secrets managers store credentials
centrally, inject them into applications at runtime, and support automatic
rotation, so a leaked secret has a limited window of validity before it is
rotated out.""",

    "doc16_llm_data_poisoning.txt": """Training Data Poisoning
Data poisoning attacks corrupt a model's training or fine-tuning data so
that the resulting model behaves incorrectly or maliciously under specific
trigger conditions, while behaving normally otherwise. In RAG systems, a
related risk is corpus poisoning, where an attacker inserts crafted
documents into the retrieval corpus itself so that they get retrieved and
influence the model's output, without ever touching the model's weights.""",

    "doc17_container_image_scanning.txt": """Container Image Scanning
Scanning container images for known vulnerabilities (CVEs) in their base
image and installed packages should happen before deployment, typically as
part of the CI/CD pipeline. Image scanning tools compare installed package
versions against vulnerability databases and can block a build from being
pushed to a registry if it contains packages above a configured severity
threshold, catching vulnerable dependencies before they reach production.""",

    "doc18_logging_and_detection.txt": """Centralized Logging and Detection
Centralized logging aggregates logs from across cloud services, applications,
and infrastructure into a single searchable system, which is a prerequisite
for effective detection. Detection rules and alerts are only as good as the
log coverage feeding them; a common gap is missing data-plane logs (like
object-level S3 access), which leaves entire categories of malicious
activity invisible to the security team despite control-plane logging being
enabled.""",
}


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "corpus")
    os.makedirs(out_dir, exist_ok=True)

    for filename, content in CORPUS.items():
        path = os.path.join(out_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip())

    print(f"✅ Wrote {len(CORPUS)} documents to {out_dir}")


if __name__ == "__main__":
    main()