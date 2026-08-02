import os
import pickle
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi

from utils.loaders import load_documents
from utils.cleaner import clean_text


# ===========================================
# CONFIG
# ===========================================

DATA_FOLDER = "uploads"

VECTOR_FOLDER = "vector_store"

MODEL_NAME = "all-MiniLM-L6-v2"


# ===========================================
# LOAD DOCUMENTS
# ===========================================

print("\nLoading Documents...\n")

documents = load_documents(DATA_FOLDER)

print(f"\nDocuments Loaded : {len(documents)}")


# ===========================================
# CLEAN DOCUMENTS
# ===========================================

print("\nCleaning Documents...\n")

for doc in documents:
    doc.page_content = clean_text(doc.page_content)


# ===========================================
# SPLIT DOCUMENTS
# ===========================================

print("Splitting Documents...\n")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=200
)

chunks = splitter.split_documents(documents)

for chunk in chunks:
    if "source" in chunk.metadata:
        chunk.metadata["source"] = os.path.basename(chunk.metadata["source"])

print(f"Total Chunks : {len(chunks)}")


# ===========================================
# HANDLE EMPTY DOCUMENTS
# ===========================================

os.makedirs(VECTOR_FOLDER, exist_ok=True)

if len(chunks) == 0:

    print("\nNo documents found.")

    empty_index = faiss.IndexFlatL2(384)

    faiss.write_index(
        empty_index,
        os.path.join(VECTOR_FOLDER, "index.faiss")
    )

    with open(
        os.path.join(VECTOR_FOLDER, "chunks.pkl"),
        "wb"
    ) as f:
        pickle.dump([], f)

    with open(
        os.path.join(VECTOR_FOLDER, "bm25.pkl"),
        "wb"
    ) as f:
        pickle.dump(None, f)

    print("\nEmpty Vector Store Created!")

    exit()


# ===========================================
# EMBEDDINGS
# ===========================================

print("\nLoading Embedding Model...\n")

model = SentenceTransformer(
    MODEL_NAME,
    local_files_only=False
)

texts = [chunk.page_content for chunk in chunks]

print("Generating Embeddings...\n")

embeddings = model.encode(
    texts,
    convert_to_numpy=True,
    show_progress_bar=True
)

embeddings = embeddings.astype("float32")


# ===========================================
# BUILD FAISS
# ===========================================

print("\nBuilding FAISS Index...\n")

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

print("Vectors Stored :", index.ntotal)


# ===========================================
# BUILD BM25
# ===========================================

print("\nBuilding BM25 Index...\n")

tokenized_chunks = [

    chunk.page_content.lower().split()

    for chunk in chunks

]

bm25 = BM25Okapi(tokenized_chunks)

print("BM25 Ready.")


# ===========================================
# SAVE EVERYTHING
# ===========================================

faiss.write_index(
    index,
    os.path.join(VECTOR_FOLDER, "index.faiss")
)

with open(
    os.path.join(VECTOR_FOLDER, "chunks.pkl"),
    "wb"
) as f:
    pickle.dump(chunks, f)

with open(
    os.path.join(VECTOR_FOLDER, "bm25.pkl"),
    "wb"
) as f:
    pickle.dump(bm25, f)

print("\n✅ Hybrid Vector Store Created Successfully!")