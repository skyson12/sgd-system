import pytesseract
import fitz  # PyMuPDF
from PIL import Image
import io
import logging
from typing import Optional
import tempfile
import os
from tika import parser

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        self.tesseract_config = r'--oem 3 --psm 6'
        
    def is_ready(self) -> bool:
        """Check if OCR service is ready"""
        try:
            # Test Tesseract
            pytesseract.get_tesseract_version()
            return True
        except Exception as e:
            logger.error(f"OCR service not ready: {e}")
            return False
    
    async def extract_text(
        self,
        file_content: bytes,
        content_type: str,
        filename: str
    ) -> str:
        """Extract text from various file types"""
        try:
            if content_type == "application/pdf":
                return await self._extract_from_pdf(file_content)
            elif content_type.startswith("image/"):
                return await self._extract_from_image(file_content)
            elif content_type == "text/plain":
                return file_content.decode('utf-8')
            else:
                # Try with Apache Tika for other formats
                return await self._extract_with_tika(file_content)
                
        except Exception as e:
            logger.error(f"Text extraction failed for {filename}: {e}")
            raise
    
    async def _extract_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text from PDF using PyMuPDF and OCR fallback"""
        text = ""
        
        try:
            # First, try to extract text directly
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                
                # If no text found, use OCR on the page
                if not page_text.strip():
                    logger.info(f"No text found on page {page_num + 1}, using OCR")
                    
                    # Convert page to image
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    
                    # OCR the image
                    ocr_text = await self._ocr_image(img_data)
                    text += f"\n--- Page {page_num + 1} (OCR) ---\n{ocr_text}\n"
                else:
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            
            doc.close()
            return text.strip()
            
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            raise
    
    async def _extract_from_image(self, image_content: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            return await self._ocr_image(image_content)
        except Exception as e:
            logger.error(f"Image text extraction failed: {e}")
            raise
    
    async def _ocr_image(self, image_content: bytes) -> str:
        """Perform OCR on image bytes"""
        try:
            # Open image
            image = Image.open(io.BytesIO(image_content))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Perform OCR with both English and Spanish
            text = pytesseract.image_to_string(
                image,
                lang='eng+spa',
                config=self.tesseract_config
            )
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            raise
    
    async def _extract_with_tika(self, file_content: bytes) -> str:
        """Extract text using Apache Tika"""
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name
            
            try:
                # Parse with Tika
                parsed = parser.from_file(temp_path)
                text = parsed.get('content', '')
                
                if text:
                    return text.strip()
                else:
                    raise Exception("No text extracted by Tika")
                    
            finally:
                # Clean up temp file
                os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"Tika extraction failed: {e}")
            raise