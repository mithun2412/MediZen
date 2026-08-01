import os
import logging
from typing import Dict, Any, Optional
from groq import Groq  # Change to GROQ
from app.services.pdf_text_extractor import PDFTextExtractor

logger = logging.getLogger(__name__)

class LLMContextService:
    def __init__(self):
        # Use GROQ client directly
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.pdf_extractor = PDFTextExtractor()
        
    def answer_question_from_pdf(
        self,
        pdf_path: str,
        question: str,
        user_id: int = None,
        max_context_chars: int = 100000
    ) -> Dict[str, Any]:
        """
        Extract text from PDF and answer question using GROQ with full context
        """
        try:
            # Step 1: Extract all text from PDF
            extraction_result = self.pdf_extractor.extract_text_from_pdf(pdf_path)
            
            if not extraction_result['success']:
                return {
                    "success": False,
                    "error": extraction_result.get('error', 'Failed to extract text'),
                    "answer": "Could not extract text from PDF."
                }
            
            full_text = extraction_result['full_text']
            
            if not full_text.strip():
                return {
                    "success": False,
                    "error": "No text could be extracted from the PDF",
                    "answer": "The PDF appears to be empty or unreadable."
                }
            
            # Step 2: Truncate if needed
            if len(full_text) > max_context_chars:
                full_text = full_text[:max_context_chars]
                logger.warning(f"Truncated PDF text to {max_context_chars} characters")
            
            # Step 3: Create prompt with full context
            system_prompt = """You are a helpful assistant that answers questions based on the provided document content.
            Answer the user's question using ONLY the information from the document.
            If the answer is not found in the document, say so clearly.
            Provide detailed, accurate responses based on the document content."""
            
            user_prompt = f"""
            DOCUMENT CONTENT:
            {full_text}
            
            USER QUESTION:
            {question}
            
            INSTRUCTIONS:
            - Answer based ONLY on the document content above
            - Be specific and detailed
            - If the information is not in the document, say so
            - Do not make up information
            """
            
            # Step 4: Call GROQ with your exact parameters
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Lower temperature for more focused answers
                max_tokens=300    # Shorter responses for medical context
            )
            
            answer = response.choices[0].message.content
            
            return {
                "success": True,
                "answer": answer,
                "context_used": full_text[:1000] + "..." if len(full_text) > 1000 else full_text,
                "total_chars": len(full_text),
                "word_count": len(full_text.split()),
                "pages_extracted": extraction_result.get('total_pages', 0),
                "model_used": self.model,
                "tokens_used": {
                    "prompt": response.usage.prompt_tokens if hasattr(response, 'usage') else 0,
                    "completion": response.usage.completion_tokens if hasattr(response, 'usage') else 0,
                    "total": response.usage.total_tokens if hasattr(response, 'usage') else 0
                } if hasattr(response, 'usage') else {}
            }
            
        except Exception as e:
            logger.error(f"GROQ context error: {e}")
            return {
                "success": False,
                "error": str(e),
                "answer": f"Error processing your question: {str(e)}"
            }
    
    def answer_question_from_text(
        self,
        text_content: str,
        question: str,
        max_context_chars: int = 100000
    ) -> Dict[str, Any]:
        """
        Answer question from direct text content (for non-PDF uploads)
        """
        try:
            # Truncate if needed
            if len(text_content) > max_context_chars:
                text_content = text_content[:max_context_chars]
            
            system_prompt = """You are a helpful assistant that answers questions based on the provided content.
            Answer the user's question using ONLY the information from the content.
            If the answer is not found, say so clearly."""
            
            user_prompt = f"""
            CONTENT:
            {text_content}
            
            USER QUESTION:
            {question}
            
            INSTRUCTIONS:
            - Answer based ONLY on the content above
            - Be specific and detailed
            - If the information is not in the content, say so
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            return {
                "success": True,
                "answer": response.choices[0].message.content,
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Text context error: {e}")
            return {
                "success": False,
                "error": str(e),
                "answer": f"Error processing your question: {str(e)}"
            }