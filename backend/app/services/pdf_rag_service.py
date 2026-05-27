import faiss
import numpy as np

from pypdf import PdfReader

from sentence_transformers import (
    SentenceTransformer
)

from app.llm.groq_client import client


# ─────────────────────────────────────────────
# LOAD EMBEDDING MODEL
# ─────────────────────────────────────────────

embedding_model = SentenceTransformer(

    "all-MiniLM-L6-v2"
)

# ─────────────────────────────────────────────
# GLOBAL VECTOR STORE
# ─────────────────────────────────────────────

document_chunks = []

vector_index = None


# ─────────────────────────────────────────────
# READ PDF
# ─────────────────────────────────────────────

def extract_pdf_text(

    pdf_path: str
):

    text = ""

    reader = PdfReader(
        pdf_path
    )

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:

            text += extracted + "\n"

    return text


# ─────────────────────────────────────────────
# CHUNK TEXT
# ─────────────────────────────────────────────

def chunk_text(

    text: str,

    chunk_size: int = 500
):

    chunks = []

    for i in range(

        0,

        len(text),

        chunk_size
    ):

        chunk = text[
            i:i + chunk_size
        ]

        chunks.append(chunk)

    return chunks


# ─────────────────────────────────────────────
# CREATE VECTOR STORE
# ─────────────────────────────────────────────

def build_vector_store(

    pdf_path: str
):

    global document_chunks
    global vector_index

    # EXTRACT TEXT
    text = extract_pdf_text(
        pdf_path
    )

    # CHUNKS
    document_chunks = chunk_text(
        text
    )

    # EMBEDDINGS
    embeddings = embedding_model.encode(
        document_chunks
    )

    embeddings = np.array(
        embeddings
    ).astype("float32")

    # FAISS INDEX
    dimension = embeddings.shape[1]

    vector_index = faiss.IndexFlatL2(
        dimension
    )

    vector_index.add(embeddings)

    return {

        "success": True,

        "chunks":
            len(document_chunks)
    }


# ─────────────────────────────────────────────
# RETRIEVE RELEVANT CHUNKS
# ─────────────────────────────────────────────

def retrieve_relevant_chunks(

    query: str,

    top_k: int = 3
):

    global vector_index
    global document_chunks

    if vector_index is None:

        return []

    # QUERY EMBEDDING
    query_embedding = embedding_model.encode(
        [query]
    )

    query_embedding = np.array(
        query_embedding
    ).astype("float32")

    # SEARCH
    distances, indices = vector_index.search(

        query_embedding,

        top_k
    )

    results = []

    for idx in indices[0]:

        if idx < len(document_chunks):

            results.append(
                document_chunks[idx]
            )

    return results


# ─────────────────────────────────────────────
# AI PDF QUESTION ANSWERING
# ─────────────────────────────────────────────

def ask_pdf_question(

    question: str
):

    try:

        relevant_chunks = (

            retrieve_relevant_chunks(
                question
            )
        )

        context = "\n\n".join(
            relevant_chunks
        )

        prompt = f"""

You are MediZen AI.

Use the following medical report
context to answer the question.

Medical Report Context:

{context}

Question:
{question}

IMPORTANT:
- Answer ONLY from report context.
- If information is missing,
  say it is unavailable.
- Explain medical terms simply.
- Be medically informative.

"""

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[

                {
                    "role": "system",

                    "content": prompt
                }
            ],

            temperature=0.2,

            max_tokens=500,
        )

        answer = (

            response
            .choices[0]
            .message
            .content
            .strip()
        )

        return {

            "success": True,

            "answer": answer,

            "context":
                relevant_chunks
        }

    except Exception as e:

        print(
            "PDF RAG Error:",
            e
        )

        return {

            "success": False,

            "answer":

                "Unable to analyze PDF.",

            "context": []
        }