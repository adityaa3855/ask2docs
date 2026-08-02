import os

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename


# =====================================================
# Flask App
# =====================================================

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =====================================================
# Home
# =====================================================

@app.route("/")
def home():

    return render_template("index.html")


# =====================================================
# Ask AI
# =====================================================

@app.route("/ask", methods=["POST"])
def ask():

    try:

        data = request.get_json()

        question = data.get("question", "").strip()

        if question == "":

            return jsonify({

                "success": False,

                "message": "Question cannot be empty."

            }), 400

        from retriever import retrieve
        from llm import generate_answer

        chunks = retrieve(question)

        answer = generate_answer(question, chunks)

        sources = []

        seen = set()

        for chunk in chunks:

            source = chunk.metadata.get("source", "Unknown")

            page = chunk.metadata.get("page", 0) + 1

            key = (source, page)

            if key not in seen:

                seen.add(key)

                sources.append({

                    "file": source,

                    "page": page

                })

        return jsonify({

            "success": True,

            "question": question,

            "answer": answer,

            "sources": sources

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


# =====================================================
# Upload Documents
# =====================================================

@app.route("/upload", methods=["POST"])
def upload():

    try:

        if "files" not in request.files:

            return jsonify({

                "success": False,

                "message": "No files received."

            }), 400

        files = request.files.getlist("files")

        uploaded_files = []

        for file in files:

            if file.filename == "":

                continue

            filename = secure_filename(file.filename)

            filepath = os.path.join(UPLOAD_FOLDER, filename)

            file.save(filepath)

            uploaded_files.append(filename)

        print("\nUploaded Files:")

        for file in uploaded_files:

            print(file)

        print("\nRebuilding Vector Store...\n")

        from ingest import run_ingestion
        run_ingestion()

        print("\nVector Store Updated Successfully!\n")

        return jsonify({

            "success": True,

            "message": "Documents uploaded successfully.",

            "files": uploaded_files

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


# =====================================================
# Run Server
# =====================================================
# =====================================================
# Get Uploaded Documents
# =====================================================

@app.route("/documents", methods=["GET"])
def get_documents():

    files = []
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    for file in os.listdir(UPLOAD_FOLDER):

        if file.lower().endswith((".pdf", ".txt", ".docx")):

            files.append(file)

    files.sort()

    return jsonify({

        "success": True,

        "documents": files

    })



# =====================================================
# Delete Document
# =====================================================

@app.route("/delete/<filename>", methods=["DELETE"])
def delete_document(filename):

    try:

        filepath = os.path.join("uploads", filename)

        if not os.path.exists(filepath):

            return jsonify({

                "success": False,

                "message": "File not found."

            }), 404

        os.remove(filepath)

        print(f"\nDeleted : {filename}")

        print("Rebuilding Vector Store...")

        from ingest import run_ingestion
        run_ingestion()

        print("Done!")

        return jsonify({

            "success": True,

            "message": "Document deleted successfully."

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500






if __name__ == "__main__":

    app.run(debug=True)