# app/routes/upload.py

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Form,
    Depends
)
from sqlalchemy.orm import Session
from typing import Optional
import os
import shutil
import base64
from datetime import datetime
import logging
from PIL import Image
import pytesseract
import fitz
import io
import traceback
import json
import re

from app.core.database import get_db  # ✅ NEW
from app.models.models import Conversation, Report
from app.services.ai_memory_service import create_conversation, save_message, get_conversation_messages

logger = logging.getLogger(__name__)
router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("reports", exist_ok=True)

# ─────────────────────────────────────────────
# TEXT EXTRACTORS WITH ERROR HANDLING
# ─────────────────────────────────────────────

def extract_text_from_pdf(pdf_path: str) -> dict:
    """Extract all text from PDF with OCR for images"""
    try:
        logger.info(f"Extracting text from PDF: {pdf_path}")
        doc = fitz.open(pdf_path)
        all_text = []
        total_pages = len(doc)
        image_pages = 0
        text_pages = 0
        
        for page_num in range(total_pages):
            try:
                page = doc[page_num]
                page_text = page.get_text()
                images = page.get_images(full=True)
                
                if len(images) > 0 and len(page_text.strip()) < 100:
                    image_pages += 1
                    logger.info(f"Page {page_num + 1} has images, running OCR...")
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img_data = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_data))
                    ocr_text = pytesseract.image_to_string(image, lang='eng')
                    page_text = ocr_text
                else:
                    text_pages += 1
                
                if page_text.strip():
                    all_text.append(page_text.strip())
            except Exception as e:
                logger.error(f"Error processing page {page_num + 1}: {e}")
                continue
        
        doc.close()
        full_text = "\n\n".join(all_text)
        
        # Check if text has meaningful content
        has_text = has_meaningful_text(full_text)
        
        return {
            "success": True,
            "full_text": full_text,
            "total_pages": total_pages,
            "text_pages": text_pages,
            "image_pages": image_pages,
            "total_characters": len(full_text),
            "word_count": len(full_text.split()),
            "has_text": has_text,
            "is_image_only": not has_text and total_pages > 0  # PDF with only images
        }
        
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e), "full_text": "", "has_text": False, "is_image_only": False}

def extract_text_from_image(image_path: str) -> dict:
    """Extract text from image using OCR and determine if image has meaningful text"""
    try:
        logger.info(f"Extracting text from image: {image_path}")
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang='eng')
        
        # Check if text contains meaningful content
        has_text = has_meaningful_text(text)
        
        # Log the extracted text for debugging
        logger.info(f"Extracted text length: {len(text)}, Has text: {has_text}")
        if text:
            logger.info(f"Text preview: {text[:100]}...")
        
        return {
            "success": True,
            "full_text": text,
            "total_characters": len(text),
            "word_count": len(text.split()),
            "has_text": has_text,
            "is_image_only": not has_text  # Image with no text
        }
        
    except Exception as e:
        logger.error(f"Image extraction error: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e), "full_text": "", "has_text": False, "is_image_only": True}

def has_meaningful_text(text: str) -> bool:
    """Check if extracted text has meaningful content"""
    if not text or len(text.strip()) < 20:
        return False
    
    # Remove special characters and check for real words
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    words = cleaned.split()
    
    # Check if there are enough real words (at least 10)
    if len(words) < 10:
        return False
    
    # Check if text has sentence structure
    sentences = re.split(r'[.!?]+', text)
    if len(sentences) > 2:
        return True
    
    # Check for common document text patterns
    document_patterns = [
        r'(?i)patient',
        r'(?i)diagnosis',
        r'(?i)treatment',
        r'(?i)prescription',
        r'(?i)medical',
        r'(?i)report',
        r'(?i)history',
        r'(?i)symptoms?',
        r'(?i)condition',
        r'(?i)recommend',
        r'(?i)doctor',
        r'(?i)hospital',
        r'(?i)clinical',
        r'(?i)laboratory',
        r'(?i)test',
        r'(?i)result',
        r'(?i)date',
        r'(?i)name',
        r'(?i)age',
        r'(?i)gender'
    ]
    
    for pattern in document_patterns:
        if re.search(pattern, text):
            return True
    
    return False

def encode_image_to_base64(image_path: str) -> str:
    """Encode image to base64 for API calls"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image: {e}")
        return None

# ─────────────────────────────────────────────
# MEDICAL IMAGE ANALYSIS USING VISION
# ─────────────────────────────────────────────

def analyze_medical_image_with_vision(image_path: str, question: str) -> dict:
    """Analyze medical image using Gemini or GPT-4 Vision"""
    try:
        logger.info(f"Analyzing medical image with vision: {image_path}")
        
        # Try Gemini first
        try:
            from google import genai
            from PIL import Image
            
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                logger.info("Using Gemini Vision for medical image analysis")
                client = genai.Client(api_key=gemini_api_key)
                image = Image.open(image_path)
                
                prompt = f"""Analyze this medical image carefully.

Answer this question: {question}

Please provide a comprehensive analysis including:
1. What is visible in the image (describe the appearance, location, characteristics)
2. Possible conditions or findings (with clear uncertainty and disclaimers)
3. Severity indicators (mild, moderate, severe)
4. Skin appearance details (color, texture, shape, size)
5. Signs of infection if any
6. Home care recommendations
7. When to consult a doctor

Important Guidelines:
- Do NOT provide a definitive diagnosis
- Always include a medical disclaimer
- Use patient-friendly language
- Clearly mention uncertainty
- Be specific about what you observe
"""
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[prompt, image]
                )
                
                logger.info("Gemini Vision analysis successful")
                return {
                    "success": True,
                    "answer": response.text,
                    "model_used": "gemini-2.5-flash-vision",
                    "vision_enabled": True
                }
                
        except ImportError:
            logger.warning("Gemini SDK not installed")
        except Exception as e:
            logger.warning(f"Gemini Vision failed: {e}, trying GPT-4 Vision")
        
        # Fallback to GPT-4 Vision
        try:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                from openai import OpenAI
                client = OpenAI(api_key=openai_api_key)
                
                base64_image = encode_image_to_base64(image_path)
                if not base64_image:
                    raise Exception("Failed to encode image")
                
                system_prompt = """You are MediZen AI, a medical assistant specializing in dermatology and skin conditions.
Analyze the image carefully and provide helpful information.
Always include a medical disclaimer.
Never provide a definitive diagnosis."""
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"""{system_prompt}
                                    
Analyze this medical image and answer:
{question}

Please provide:
1. Visual observations (appearance, location, characteristics)
2. Possible conditions (with uncertainty)
3. Severity indicators
4. Home care recommendations
5. When to consult a doctor
6. Clear medical disclaimer
"""
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
                
                logger.info("GPT-4 Vision analysis successful")
                return {
                    "success": True,
                    "answer": response.choices[0].message.content,
                    "model_used": "gpt-4o-vision",
                    "vision_enabled": True
                }
                
        except Exception as e:
            logger.warning(f"GPT-4 Vision failed: {e}")
        
        # If all vision models fail, provide guidance
        logger.warning("No vision models available, providing guidance")
        return {
            "success": True,
            "answer": """I can see you've uploaded a medical image for analysis.

🔍 **Image Analysis Required**

To properly analyze this image, I need vision capabilities which are currently unavailable. However, I can help you better if you describe what you see:

**Please describe the image:**
1. **What do you observe?**
   - Color (red, brown, white, black, etc.)
   - Shape (circular, irregular, raised, flat)
   - Size (small spot, large patch)
   - Texture (scaly, smooth, bumpy, blistered)

2. **Where is it located?**
   - Face, arms, legs, torso, etc.

3. **Symptoms:**
   - Itchy, painful, burning, or no sensation
   - When did it start?
   - Has it changed over time?

4. **Additional context:**
   - Any other symptoms (fever, fatigue)?
   - Have you tried any treatments?
   - Any known allergies or conditions?

**⚠️ Important Medical Disclaimer:** 
This is NOT a medical diagnosis. Please consult a qualified healthcare provider for proper evaluation and treatment.

**Next Steps:**
1. Describe the image in detail above
2. I'll help analyze based on your description
3. Always consult a doctor for proper diagnosis

Would you like to describe the image so I can help you better?""",
            "model_used": "guidance",
            "vision_enabled": False
        }
        
    except Exception as e:
        logger.error(f"Medical image analysis error: {e}")
        return {
            "success": False,
            "error": str(e),
            "answer": "Unable to analyze medical image. Please try again or describe your condition in text."
        }

# ─────────────────────────────────────────────
# ANSWER QUESTION WITH CONTEXT (UPDATED - FIXED)
# ─────────────────────────────────────────────

def answer_with_context(text_content: str, question: str, image_path: Optional[str] = None, is_image_file: bool = False) -> dict:
    """Answer question using the extracted text content with GROQ"""
    try:
        logger.info(f"Answer with context - Image path: {image_path}, Is image file: {is_image_file}")
        logger.info(f"Text content length: {len(text_content)}, Has text: {has_meaningful_text(text_content)}")
        
        # CRITICAL FIX: Check if this is an image file that should use vision
        # Check both the image_path and the is_image_file flag
        should_use_vision = False
        
        if image_path and is_image_file:
            # Check if it's an image file
            image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
            is_image = image_path.lower().endswith(image_extensions)
            
            # Check if image has meaningful text
            has_text = has_meaningful_text(text_content)
            
            # Use vision if:
            # 1. It's an image file AND
            # 2. It doesn't have meaningful text OR we should use vision anyway for medical images
            if is_image:
                if not has_text:
                    logger.info("Image has no meaningful text - using vision analysis")
                    should_use_vision = True
                else:
                    # Even if it has some text, we might want to analyze the image
                    # Check if question is about the image itself
                    image_keywords = ['image', 'picture', 'photo', 'see', 'look', 'appearance', 'visual', 'skin', 'rash', 'wound', 'lesion']
                    question_lower = question.lower()
                    if any(keyword in question_lower for keyword in image_keywords):
                        logger.info("Question is about image content - using vision analysis")
                        should_use_vision = True
        
        if should_use_vision:
            logger.info("Using vision capabilities for image analysis")
            return analyze_medical_image_with_vision(image_path, question)
        
        # Regular text-based analysis
        logger.info("Using text-based analysis")
        from groq import Groq
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY not set")
            return {
                "success": False,
                "error": "GROQ API key not configured",
                "answer": "The GROQ API key is not configured. Please check your environment variables."
            }
        
        client = Groq(api_key=api_key)
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        max_chars = 80000
        if len(text_content) > max_chars:
            text_content = text_content[:max_chars]
            logger.warning(f"Truncated text to {max_chars} characters")
        
        system_prompt = """You are a helpful assistant. Answer questions based ONLY on the provided document content.
        If the answer is not in the document, say so clearly. Be specific and detailed."""
        
        user_prompt = f"""
        DOCUMENT CONTENT:
        {text_content}
        
        QUESTION:
        {question}
        
        Answer based only on the document content above. If the information isn't there, say so.
        """
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        
        return {
            "success": True,
            "answer": answer,
            "model_used": model,
            "tokens_used": {
                "prompt": response.usage.prompt_tokens if hasattr(response, 'usage') else 0,
                "completion": response.usage.completion_tokens if hasattr(response, 'usage') else 0,
                "total": response.usage.total_tokens if hasattr(response, 'usage') else 0
            } if hasattr(response, 'usage') else {},
            "vision_enabled": False
        }
        
    except ImportError:
        # Fallback: Try using OpenAI client with GROQ endpoint
        try:
            logger.warning("GROQ SDK not installed, trying OpenAI client with GROQ endpoint...")
            from openai import OpenAI
            
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return {
                    "success": False,
                    "error": "GROQ API key not configured",
                    "answer": "API key not configured."
                }
            
            client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key
            )
            model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
            
            max_chars = 80000
            if len(text_content) > max_chars:
                text_content = text_content[:max_chars]
            
            system_prompt = """You are a helpful assistant. Answer questions based ONLY on the provided document content.
            If the answer is not in the document, say so clearly. Be specific and detailed."""
            
            user_prompt = f"""
            DOCUMENT CONTENT:
            {text_content}
            
            QUESTION:
            {question}
            
            Answer based only on the document content above. If the information isn't there, say so.
            """
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            return {
                "success": True,
                "answer": answer,
                "model_used": model,
                "tokens_used": {
                    "prompt": response.usage.prompt_tokens if hasattr(response, 'usage') else 0,
                    "completion": response.usage.completion_tokens if hasattr(response, 'usage') else 0,
                    "total": response.usage.total_tokens if hasattr(response, 'usage') else 0
                } if hasattr(response, 'usage') else {},
                "vision_enabled": False
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "Neither GROQ SDK nor OpenAI package installed",
                "answer": "Please install groq: pip install groq"
            }
        except Exception as e:
            logger.error(f"OpenAI client with GROQ error: {e}")
            return {
                "success": False,
                "error": str(e),
                "answer": f"Error: {str(e)}"
            }
            
    except Exception as e:
        logger.error(f"Answer with context error: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e), "answer": f"Error: {str(e)}"}

# ─────────────────────────────────────────────
# UPLOAD AND ASK FIRST QUESTION (UPDATED - FIXED)
# ─────────────────────────────────────────────

@router.post("/upload-and-ask")
async def upload_and_ask(
    file: UploadFile = File(...),
    question: str = Form(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload a file and immediately ask the first question
    """
    try:
        logger.info(f"Upload and ask request: {file.filename}, user_id: {user_id}")
        logger.info(f"First question: {question[:100]}...")
        
        # Determine file type
        is_pdf = file.content_type == "application/pdf"
        is_image = file.content_type.startswith("image/")
        
        if not is_pdf and not is_image:
            raise HTTPException(400, "Only PDF and image files allowed")
        
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if is_pdf:
            filename = f"pdf_{timestamp}.pdf"
        else:
            ext = os.path.splitext(file.filename)[1]
            filename = f"img_{timestamp}{ext}"
        
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        logger.info(f"Saving file to: {file_path}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract content based on file type
        if is_pdf:
            result = extract_text_from_pdf(file_path)
            report_type = "pdf"
        else:
            result = extract_text_from_image(file_path)
            report_type = "image"
        
        if not result['success']:
            logger.error(f"Extraction failed: {result.get('error')}")
            return {
                "success": False,
                "error": result.get('error'),
                "message": "Failed to extract content from file"
            }
        
        has_text = result.get('has_text', False)
        is_image_only = result.get('is_image_only', False)
        
        logger.info(f"File analysis - Has text: {has_text}, Is image only: {is_image_only}")
        
        # Create report
        report_id = f"{report_type}_{timestamp}"
        report = Report(
            id=report_id,
            user_id=user_id,
            title=file.filename,
            file_path=file_path,
            content=result['full_text'],
            created_at=datetime.now()
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        
        # Create conversation
        conv = Conversation(
            user_id=user_id,
            title=f"Q&A - {file.filename}",
            created_at=datetime.now()
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conversation_id = conv.id
        logger.info(f"New conversation created: {conversation_id}")
        
        # Save user question
        save_message(
            db=db,
            conversation_id=conversation_id,
            role="user",
            content=question
        )
        
        # Get answer using the extracted content
        # CRITICAL FIX: Pass is_image flag to enable vision analysis
        answer_result = answer_with_context(
            text_content=report.content,
            question=question,
            image_path=file_path if is_image else None,
            is_image_file=is_image  # Pass this flag to enable vision
        )
        
        if not answer_result['success']:
            error_msg = answer_result.get('answer', 'Failed to get answer')
            save_message(
                db=db,
                conversation_id=conversation_id,
                role="assistant",
                content=f"Error: {error_msg}"
            )
            return {
                "success": False,
                "conversation_id": conversation_id,
                "report_id": report_id,
                "error": answer_result.get('error'),
                "answer": error_msg
            }
        
        # Save AI response
        save_message(
            db=db,
            conversation_id=conversation_id,
            role="assistant",
            content=answer_result['answer']
        )
        
        logger.info(f"First question answered successfully")
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "report_id": report_id,
            "filename": file.filename,
            "file_type": report_type,
            "question": question,
            "answer": answer_result['answer'],
            "model_used": answer_result.get('model_used'),
            "vision_enabled": answer_result.get('vision_enabled', False),
            "has_text_content": has_text,
            "is_image_only": is_image_only,
            "total_characters": result.get('total_characters', 0),
            "word_count": result.get('word_count', 0),
            "text_preview": result['full_text'][:300] + "..." if len(result['full_text']) > 300 else result['full_text']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload and ask error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"Error processing request: {str(e)}")

# ─────────────────────────────────────────────
# ASK QUESTION ENDPOINT (UPDATED - FIXED)
# ─────────────────────────────────────────────

@router.post("/ask")
async def ask_question(
    report_id: str = Form(...),
    question: str = Form(...),
    user_id: int = Form(...),
    conversation_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Ask a question about a parsed document/image
    """
    try:
        logger.info(f"Ask question request: report_id={report_id}, user_id={user_id}")
        logger.info(f"Question: {question[:100]}...")
        
        # Get the report
        report = db.query(Report).filter(Report.id == report_id).first()
        
        if not report:
            logger.error(f"Report not found: {report_id}")
            return {
                "success": False,
                "error": "Report not found",
                "answer": "The document you're asking about was not found."
            }
        
        logger.info(f"Report found. Content length: {len(report.content)}")
        
        # Check if this is an image
        image_path = None
        is_image = False
        
        if report.file_path:
            image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
            is_image = report.file_path.lower().endswith(image_extensions)
            if is_image:
                image_path = report.file_path
                logger.info(f"This is an image file: {image_path}")
        
        # Create conversation if needed
        if not conversation_id:
            conv = Conversation(
                user_id=user_id,
                title=f"Q&A - {report.title}",
                created_at=datetime.now()
            )
            db.add(conv)
            db.commit()
            db.refresh(conv)
            conversation_id = conv.id
            logger.info(f"New conversation created: {conversation_id}")
        
        # Save user question
        save_message(
            db=db,
            conversation_id=conversation_id,
            role="user",
            content=question
        )
        
        # Answer using the extracted content
        # CRITICAL FIX: Pass is_image flag to enable vision
        result = answer_with_context(
            text_content=report.content,
            question=question,
            image_path=image_path,
            is_image_file=is_image  # Pass the flag
        )
        
        if not result['success']:
            error_msg = result.get('answer', 'Failed to get answer')
            logger.error(f"Answer generation failed: {error_msg}")
            save_message(
                db=db,
                conversation_id=conversation_id,
                role="assistant",
                content=f"Error: {error_msg}"
            )
            return {
                "success": False,
                "conversation_id": conversation_id,
                "error": result.get('error'),
                "answer": error_msg
            }
        
        # Save AI response
        save_message(
            db=db,
            conversation_id=conversation_id,
            role="assistant",
            content=result['answer']
        )
        
        logger.info(f"Answer generated successfully. Vision used: {result.get('vision_enabled', False)}")
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "report_id": report_id,
            "question": question,
            "answer": result['answer'],
            "model_used": result.get('model_used'),
            "vision_enabled": result.get('vision_enabled', False),
            "tokens_used": result.get('tokens_used', {})
        }
        
    except Exception as e:
        logger.error(f"Ask question error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"Error answering question: {str(e)}")

# ... (rest of the endpoints remain the same - PDF parse, Image parse, etc.)
# ─────────────────────────────────────────────
# GET CONVERSATION
# ─────────────────────────────────────────────

@router.get("/conversation/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """
    Get conversation history
    """
    try:
        messages = get_conversation_messages(
            db=db,
            conversation_id=conversation_id
        )
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "messages": messages
        }
        
    except Exception as e:
        logger.error(f"Get conversation error: {e}")
        raise HTTPException(500, str(e))

# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Document Q&A Service",
        "timestamp": datetime.now().isoformat()
    }

# ─────────────────────────────────────────────
# PDF PARSE ENDPOINT
# ─────────────────────────────────────────────

@router.post("/pdf/parse")
async def parse_pdf(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload and parse a PDF - extracts all text with OCR for images
    """
    try:
        logger.info(f"PDF parse request received: {file.filename}, user_id: {user_id}")
        
        # Validate file type
        if file.content_type != "application/pdf":
            logger.error(f"Invalid file type: {file.content_type}")
            raise HTTPException(400, "Only PDF files allowed")
        
        # Save PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pdf_{timestamp}.pdf"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        logger.info(f"Saving PDF to: {file_path}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text
        logger.info("Extracting text from PDF...")
        result = extract_text_from_pdf(file_path)
        
        if not result['success']:
            logger.error(f"Text extraction failed: {result.get('error')}")
            return {
                "success": False,
                "error": result.get('error'),
                "message": "Failed to extract text from PDF"
            }
        
        logger.info(f"Text extraction successful. Pages: {result['total_pages']}, Words: {result['word_count']}")
        
        # Create report in database
        report_id = f"pdf_{timestamp}"
        report = Report(
            id=report_id,
            user_id=user_id,
            title=file.filename,
            file_path=file_path,
            content=result['full_text'],
            created_at=datetime.now()
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        
        logger.info(f"Report created with ID: {report_id}")
        
        return {
            "success": True,
            "message": "PDF parsed successfully",
            "report_id": report.id,
            "filename": file.filename,
            "total_pages": result['total_pages'],
            "text_pages": result['text_pages'],
            "image_pages": result['image_pages'],
            "total_characters": result['total_characters'],
            "word_count": result['word_count'],
            "has_text": result.get('has_text', False),
            "text_preview": result['full_text'][:500] + "..." if len(result['full_text']) > 500 else result['full_text']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF parse error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"Error parsing PDF: {str(e)}")

# ─────────────────────────────────────────────
# IMAGE PARSE ENDPOINT (UPDATED)
# ─────────────────────────────────────────────

@router.post("/image/parse")
async def parse_image(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload and parse an image - OCR to extract text
    """
    try:
        logger.info(f"Image parse request received: {file.filename}, user_id: {user_id}")
        
        # Validate file type
        if not file.content_type.startswith("image/"):
            logger.error(f"Invalid file type: {file.content_type}")
            raise HTTPException(400, "Only image files allowed")
        
        # Save image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = os.path.splitext(file.filename)[1]
        filename = f"img_{timestamp}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        logger.info(f"Saving image to: {file_path}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text with OCR
        logger.info("Extracting text from image with OCR...")
        result = extract_text_from_image(file_path)
        
        if not result['success']:
            logger.error(f"OCR failed: {result.get('error')}")
            return {
                "success": False,
                "error": result.get('error'),
                "message": "Failed to extract text from image"
            }
        
        logger.info(f"OCR successful. Words: {result['word_count']}")
        
        # Create report in database
        report_id = f"img_{timestamp}"
        report = Report(
            id=report_id,
            user_id=user_id,
            title=file.filename,
            file_path=file_path,
            content=result['full_text'],
            created_at=datetime.now()
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        
        logger.info(f"Report created with ID: {report_id}")
        
        return {
            "success": True,
            "message": "Image parsed successfully",
            "report_id": report.id,
            "filename": file.filename,
            "total_characters": result['total_characters'],
            "word_count": result['word_count'],
            "has_text": result.get('has_text', False),
            "text_preview": result['full_text'][:500] + "..." if len(result['full_text']) > 500 else result['full_text']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image parse error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"Error parsing image: {str(e)}")

# ─────────────────────────────────────────────
# LEGACY ENDPOINTS (for backward compatibility)
# ─────────────────────────────────────────────

@router.post("/pdf")
async def upload_legacy_pdf(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Legacy PDF upload - redirects to /pdf/parse"""
    return await parse_pdf(file, user_id, db)

@router.post("/image")
async def upload_legacy_image(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """Legacy image upload - redirects to /image/parse"""
    return await parse_image(file, user_id, db)

@router.post("/pdf/chat")
async def legacy_pdf_chat(
    report_id: str = Form(...),
    question: str = Form(...),
    user_id: int = Form(...),
    conversation_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """Legacy PDF chat - redirects to /ask"""
    return await ask_question(report_id, question, user_id, conversation_id, db)