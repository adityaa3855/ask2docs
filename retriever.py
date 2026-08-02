import os
import pickle
import numpy as np


# ==========================================
# LAZY LOAD MODEL
# ==========================================

model = None


def get_model():
    global model

    if model is None:
        print("Loading Embedding Model...")

        from fastembed import TextEmbedding
        model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

    return model


# ==========================================
# RETRIEVER
# ==========================================

def retrieve(query, faiss_k=5, bm25_k=5):

    # ==========================================
    # LOAD INDEXES
    # ==========================================

    os.makedirs("vector_store", exist_ok=True)

    if (
        not os.path.exists(os.path.join("vector_store", "index.faiss"))
        or not os.path.exists(os.path.join("vector_store", "chunks.pkl"))
        or not os.path.exists(os.path.join("vector_store", "bm25.pkl"))
    ):
        return []

    import faiss
    print("Loading Latest FAISS Index...")

    index = faiss.read_index(
        os.path.join("vector_store", "index.faiss")
    )

    print("Loading Latest Chunks...")

    with open(
        os.path.join("vector_store", "chunks.pkl"),
        "rb"
    ) as f:
        chunks = pickle.load(f)

    if not chunks:
        return []

    print("Loading BM25 Index...")

    with open(
        os.path.join("vector_store", "bm25.pkl"),
        "rb"
    ) as f:
        bm25 = pickle.load(f)

    # ==========================================
    # LOAD MODEL ONLY WHEN NEEDED
    # ==========================================

    model = get_model()

    # ==========================================
    # FAISS SEARCH
    # ==========================================

    query_embedding = np.array(list(model.embed([query]))).astype("float32")

    distances, indices = index.search(query_embedding, faiss_k)

    # ==========================================
    # BM25 SEARCH
    # ==========================================

    tokenized_query = query.lower().split()

    bm25_scores = bm25.get_scores(tokenized_query)

    bm25_indices = np.argsort(bm25_scores)[::-1][:bm25_k]

    # ==========================================
    # MERGE RESULTS
    # ==========================================

    retrieved_chunks = []

    visited = set()

    print("\n================ HYBRID SEARCH RESULTS ================\n")

    print("\n------ FAISS RESULTS ------")

    for i, (distance, idx) in enumerate(
        zip(distances[0], indices[0]),
        start=1
    ):

        if idx == -1:
            continue

        if idx in visited:
            continue

        visited.add(idx)

        print(f"\nFAISS Result {i}")
        print(f"Distance : {distance}")
        print("Source :", chunks[idx].metadata.get("source"))
        print("Page :", chunks[idx].metadata.get("page", 0) + 1)
        print("-" * 60)
        print(chunks[idx].page_content[:300])
        print("-" * 60)

        retrieved_chunks.append(chunks[idx])

    print("\n------ BM25 RESULTS ------")

    for i, idx in enumerate(bm25_indices, start=1):

        if idx in visited:
            continue

        visited.add(idx)

        print(f"\nBM25 Result {i}")
        print(f"Score : {bm25_scores[idx]}")
        print("Source :", chunks[idx].metadata.get("source"))
        print("Page :", chunks[idx].metadata.get("page", 0) + 1)
        print("-" * 60)
        print(chunks[idx].page_content[:300])
        print("-" * 60)

        retrieved_chunks.append(chunks[idx])

    return retrieved_chunks