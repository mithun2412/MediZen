from sentence_transformers import (
    SentenceTransformer
)

import chromadb


# ─────────────────────────────────────────────
# LOAD EMBEDDING MODEL
# ─────────────────────────────────────────────

embedding_model = SentenceTransformer(

    "all-MiniLM-L6-v2"
)


# ─────────────────────────────────────────────
# INIT CHROMADB
# ─────────────────────────────────────────────

client = chromadb.PersistentClient(

    path="app/memory/chroma_db"
)

collection = client.get_or_create_collection(

    name="patient_memory"
)


# ─────────────────────────────────────────────
# STORE MEMORY
# ─────────────────────────────────────────────

def store_memory(

    user_id: int,

    text: str,

    metadata: dict = None
):

    embedding = embedding_model.encode(

        text
    ).tolist()

    memory_id = f"{user_id}_{hash(text)}"

    collection.add(

        ids=[memory_id],

        embeddings=[embedding],

        documents=[text],

        metadatas=[

            metadata or {}
        ]
    )

    return {

        "success": True,

        "memory_id": memory_id
    }


# ─────────────────────────────────────────────
# SEARCH MEMORY
# ─────────────────────────────────────────────

def search_memory(

    query: str,

    top_k: int = 3
):

    query_embedding = embedding_model.encode(

        query
    ).tolist()

    results = collection.query(

        query_embeddings=[query_embedding],

        n_results=top_k
    )

    return {

        "documents":
            results["documents"][0],

        "metadatas":
            results["metadatas"][0]
    }