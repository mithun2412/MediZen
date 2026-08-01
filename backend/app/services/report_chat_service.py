from typing import Dict, Any, List, Optional

from app.llm.groq_client import client

def ask_report_question(
    report_id: int,
    question: str,
    top_k: int = 3
) -> Dict[str, Any]:
    """
    Answer questions about a report using RAG
    """
    try:
        # Retrieve relevant chunks
        chunks = retrieve_chunks(report_id, question, top_k=top_k)
        
        if not chunks:
            return {
                "success": False,
                "error": "No relevant information found",
                "answer": "I couldn't find relevant information to answer your question."
            }
        
        # Build context
        context = "\n\n".join([chunk["chunk"] for chunk in chunks])
        
        # Get LLM response
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical assistant answering questions about medical reports and documents."
                },
                {
                    "role": "user",
                    "content": f"""
                    Context from the medical document:
                    {context}
                    
                    Question: {question}
                    
                    Please provide a clear, accurate, and helpful answer based on the context provided.
                    """
                }
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        answer = response.choices[0].message.content.strip()
        
        return {
            "success": True,
            "answer": answer,
            "context": chunks,
            "confidence": sum(chunk["score"] for chunk in chunks) / len(chunks) if chunks else 0
        }
        
    except Exception as e:
        print(f"Ask Report Question Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "answer": "Failed to answer the question. Please try again."
        }

def ask_report_rag(
    report_id: int,
    question: str,
    top_k: int = 3
) -> Dict[str, Any]:
    """
    Advanced RAG query with enhanced context handling
    """
    try:
        # Check if vectors exist
        vector_status = get_vector_status(report_id)
        
        if not vector_status.get("has_index"):
            return {
                "success": False,
                "error": "Report not indexed for RAG",
                "answer": "This report hasn't been processed for question answering yet."
            }
        
        # Retrieve relevant chunks with scores
        chunks = retrieve_chunks(report_id, question, top_k=top_k)
        
        if not chunks:
            return {
                "success": False,
                "error": "No relevant information found",
                "answer": "I couldn't find relevant information to answer your question."
            }
        
        # Prepare context with metadata
        context_parts = []
        for chunk in chunks:
            context_parts.append(f"[Chunk {chunk['index']}] (Score: {chunk['score']:.2f})\n{chunk['chunk']}")
        
        context = "\n\n".join(context_parts)
        
        # Enhanced prompt with more context
        prompt = f"""
You are MediZen AI, a medical assistant analyzing documents and reports.

DOCUMENT CONTEXT:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. Answer the question based ONLY on the provided context
2. If the context doesn't contain the answer, say "I couldn't find this information in the document"
3. Be specific and reference the document when possible
4. Provide a clear, concise, and helpful response
5. If medical advice is requested, include a disclaimer

ANSWER:
"""
        
        # Get LLM response
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a medical document analysis assistant. Always be helpful, accurate, and include appropriate medical disclaimers."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=600
        )
        
        answer = response.choices[0].message.content.strip()
        
        return {
            "success": True,
            "answer": answer,
            "context": chunks,
            "total_chunks": len(chunks),
            "avg_confidence": sum(chunk["score"] for chunk in chunks) / len(chunks) if chunks else 0,
            "report_id": report_id
        }
        
    except Exception as e:
        print(f"Ask Report RAG Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "answer": "An error occurred while processing your question. Please try again."
        }