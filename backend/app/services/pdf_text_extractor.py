import os
import logging
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
from PIL import Image
import io
import numpy as np
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class PDFTextExtractor:
    def __init__(self):
        self.ocr_enabled = True
        # Initialize PaddleOCR with English and Hindi support
        self.ocr = PaddleOCR(
            use_angle_cls=True,  # Use angle classifier for better text detection
            lang='en',  # Language: 'en', 'ch', 'korean', 'japan', 'german', 'french', etc.
            show_log=False,  # Reduce console output
            use_gpu=False,  # Set to True if you have GPU
            enable_mkldnn=True,  # Enable MKL-DNN for faster inference
            det_db_thresh=0.3,  # Detection threshold
            det_db_box_thresh=0.5,  # Box threshold
            rec_img_h=48,  # Recognition image height
            rec_algorithm='SVTR_LCNet'  # Recognition algorithm
        )
        
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract all text from PDF with PaddleOCR for image-based pages
        Returns full text content for LLM context
        """
        try:
            doc = fitz.open(pdf_path)
            all_text = []
            page_details = []
            has_images = False
            total_pages = len(doc)
            
            for page_num in range(total_pages):
                page = doc[page_num]
                
                # Try to extract text directly
                page_text = page.get_text()
                
                # Check if page has images but little text
                images = page.get_images(full=True)
                
                if len(images) > 0 and len(page_text.strip()) < 100:
                    # This page is mostly image-based - run PaddleOCR
                    has_images = True
                    logger.info(f"Page {page_num + 1} has images and little text, running PaddleOCR...")
                    
                    # Convert page to image with higher resolution for better OCR
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
                    img_data = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_data))
                    
                    # Convert PIL image to numpy array for PaddleOCR
                    img_array = np.array(image)
                    
                    # Run PaddleOCR
                    result = self.ocr.ocr(img_array, cls=True)
                    
                    # Extract text from OCR results
                    ocr_text = self._extract_text_from_ocr_result(result)
                    page_text = ocr_text
                    
                    logger.info(f"Page {page_num + 1} OCR extracted {len(ocr_text)} characters")
                    
                elif len(page_text.strip()) > 0:
                    # Page has text content
                    logger.info(f"Page {page_num + 1} has {len(page_text)} characters of text")
                
                # Clean and normalize text
                if page_text.strip():
                    cleaned_text = self._clean_text(page_text)
                    all_text.append(cleaned_text)
                    page_details.append({
                        "page": page_num + 1,
                        "text_length": len(cleaned_text),
                        "has_images": len(images) > 0,
                        "used_ocr": len(images) > 0 and len(page.get_text().strip()) < 100
                    })
            
            doc.close()
            
            # Combine all pages
            full_text = "\n\n".join(all_text)
            
            # If no text extracted at all, try OCR on all pages
            if len(full_text.strip()) == 0:
                logger.warning("No text extracted, running PaddleOCR on all pages...")
                full_text = self._ocr_all_pages(pdf_path)
                has_images = True
            
            return {
                "success": True,
                "full_text": full_text,
                "total_pages": total_pages,
                "page_details": page_details,
                "has_images": has_images,
                "total_characters": len(full_text),
                "word_count": len(full_text.split())
            }
            
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return {
                "success": False,
                "error": str(e),
                "full_text": ""
            }
    
    def _ocr_all_pages(self, pdf_path: str) -> str:
        """Fallback: OCR all pages of the PDF using PaddleOCR"""
        try:
            doc = fitz.open(pdf_path)
            all_text = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                img_array = np.array(image)
                
                # Run PaddleOCR
                result = self.ocr.ocr(img_array, cls=True)
                text = self._extract_text_from_ocr_result(result)
                all_text.append(text)
            
            doc.close()
            return "\n\n".join(all_text)
            
        except Exception as e:
            logger.error(f"OCR all pages error: {e}")
            return ""
    
    def _extract_text_from_ocr_result(self, result) -> str:
        """
        Extract text from PaddleOCR result
        Result format: [[[box], (text, confidence)], ...]
        """
        if not result or not result[0]:
            return ""
        
        text_lines = []
        for line in result[0]:
            # Each line: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]], (text, confidence)
            if line and len(line) > 1:
                text = line[1][0]  # Extract the text
                confidence = line[1][1]  # Confidence score
                if confidence > 0.5:  # Filter low confidence results
                    text_lines.append(text)
        
        return " ".join(text_lines)
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text directly from an image using PaddleOCR
        """
        try:
            image = Image.open(image_path)
            img_array = np.array(image)
            
            result = self.ocr.ocr(img_array, cls=True)
            text = self._extract_text_from_ocr_result(result)
            
            return text
            
        except Exception as e:
            logger.error(f"Image OCR error: {e}")
            return ""