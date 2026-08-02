import os

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    CSVLoader,
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader,
    UnstructuredMarkdownLoader,
)

# ==========================================
# Supported File Types
# ==========================================

SUPPORTED_EXTENSIONS = {
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
    ".docx": Docx2txtLoader,
    ".csv": CSVLoader,
    ".xlsx": UnstructuredExcelLoader,
    ".xls": UnstructuredExcelLoader,
    ".pptx": UnstructuredPowerPointLoader,
    ".md": UnstructuredMarkdownLoader,
}


# ==========================================
# Load Documents
# ==========================================

def load_documents(folder):

    documents = []

    os.makedirs(folder, exist_ok=True)

    files = sorted(os.listdir(folder))

    if not files:
        print("No files found.")
        return documents

    for file in files:

        path = os.path.join(folder, file)

        if not os.path.isfile(path):
            continue

        extension = os.path.splitext(file)[1].lower()

        if extension not in SUPPORTED_EXTENSIONS:
            print(f"Skipping Unsupported File : {file}")
            continue

        print(f"Loading {extension.upper()} : {file}")

        try:

            # TXT requires encoding
            if extension == ".txt":

                loader = TextLoader(
                    path,
                    encoding="utf-8"
                )

            # PDF
            elif extension == ".pdf":

                loader = PyPDFLoader(path)

            # DOCX
            elif extension == ".docx":

                loader = Docx2txtLoader(path)

            # CSV
            elif extension == ".csv":

                loader = CSVLoader(path)

            # Excel
            elif extension in [".xlsx", ".xls"]:

                loader = UnstructuredExcelLoader(path)

            # PowerPoint
            elif extension == ".pptx":

                loader = UnstructuredPowerPointLoader(path)

            # Markdown
            elif extension == ".md":

                loader = UnstructuredMarkdownLoader(path)

            docs = loader.load()

            for doc in docs:
                doc.metadata["source"] = path

            documents.extend(docs)

        except Exception as e:

            print(f"Failed to load {file}")
            print(e)

    return documents