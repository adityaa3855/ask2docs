import os
import pickle
import numpy as np
import gc


# ===========================================
# CONFIG
# ===========================================

DATA_FOLDER = "uploads"
VECTOR_FOLDER = "vector_store"


def run_ingestion():
    # ===========================================
    # LOAD DOCUMENTS
    # ===========================================

    from utils.loaders import load_documents
    print("\nLoading Documents...\n")
    documents = load_documents(DATA_FOLDER)
    print(f"\nDocuments Loaded : {len(documents)}")

    # ===========================================
    # CLEAN DOCUMENTS
    # ===========================================

    from utils.cleaner import clean_text
    print("\nCleaning Documents...\n")
    for doc in documents:
        doc.page_content = clean_text(doc.page_content)

    # ===========================================
    # SPLIT DOCUMENTS
    # ===========================================

    from utils.splitter import RecursiveCharacterTextSplitter
    print("Splitting Documents...\n")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)
    
    # Free documents from memory
    del documents
    gc.collect()

    for chunk in chunks:
        if "source" in chunk.metadata:
            chunk.metadata["source"] = os.path.basename(chunk.metadata["source"])

    print(f"Total Chunks : {len(chunks)}")

    # ===========================================
    # HANDLE EMPTY DOCUMENTS
    # ===========================================

    os.makedirs(VECTOR_FOLDER, exist_ok=True)

    if len(chunks) == 0:
        import faiss
        print("\nNo documents found.")
        empty_index = faiss.IndexFlatL2(384)
        faiss.write_index(
            empty_index,
            os.path.join(VECTOR_FOLDER, "index.faiss")
        )
        with open(os.path.join(VECTOR_FOLDER, "chunks.pkl"), "wb") as f:
            pickle.dump([], f)
        with open(os.path.join(VECTOR_FOLDER, "bm25.pkl"), "wb") as f:
            pickle.dump(None, f)
        print("\nEmpty Vector Store Created!")
        return

    # ===========================================
    # EMBEDDINGS
    # ===========================================

    texts = [chunk.page_content for chunk in chunks]

    print("\nLoading Embedding Model...\n")
    # Reuse single model instance from retriever to save RAM
    from retriever import get_model
    model = get_model()

    print("Generating Embeddings...\n")
    embeddings = np.array(list(model.embed(texts))).astype("float32")

    # Free texts memory
    del texts
    gc.collect()

    embeddings = embeddings.astype("float32")

    # ===========================================
    # BUILD FAISS
    # ===========================================

    import faiss
    print("\nBuilding FAISS Index...\n")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Free embeddings memory
    del embeddings
    gc.collect()

    print("Vectors Stored :", index.ntotal)

    # ===========================================
    # BUILD BM25
    # ===========================================

    from rank_bm25 import BM25Okapi
    print("\nBuilding BM25 Index...\n")
    tokenized_chunks = [
        chunk.page_content.lower().split()
        for chunk in chunks
    ]
    bm25 = BM25Okapi(tokenized_chunks)

    # Free tokenized chunks memory
    del tokenized_chunks
    gc.collect()

    print("BM25 Ready.")

    # ===========================================
    # SAVE EVERYTHING
    # ===========================================

    faiss.write_index(
        index,
        os.path.join(VECTOR_FOLDER, "index.faiss")
    )
    with open(os.path.join(VECTOR_FOLDER, "chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)
    with open(os.path.join(VECTOR_FOLDER, "bm25.pkl"), "wb") as f:
        pickle.dump(bm25, f)

    print("\n✅ Hybrid Vector Store Created Successfully!")

    # Final cleanup to ensure memory is released after ingestion
    gc.collect()


if __name__ == "__main__":
    run_ingestion()