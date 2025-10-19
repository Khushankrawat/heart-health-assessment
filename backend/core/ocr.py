"""
OCR utilities for image processing
"""

import io
from typing import Dict, Any, Optional
from PIL import Image

# Optional imports with fallbacks
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

class OCRProcessor:
    """OCR processing for health report images"""
    
    def __init__(self):
        # Configure tesseract for better medical text recognition
        self.tesseract_config = '--oem 3 --psm 6'
    
    def extract_text_from_image(self, image_content: bytes) -> str:
        """
        Extract text from image using OCR
        
        Args:
            image_content: Image file content as bytes
            
        Returns:
            Extracted text string
        """
        try:
            if not PYTESSERACT_AVAILABLE:
                print("Warning: pytesseract not available, OCR functionality disabled")
                return ""
                
            # Open image
            image = Image.open(io.BytesIO(image_content))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image, config=self.tesseract_config)
            
            return text
            
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""
    
    def preprocess_image(self, image_content: bytes) -> bytes:
        """
        Preprocess image for better OCR results
        
        Args:
            image_content: Original image content
            
        Returns:
            Preprocessed image content
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_content))
            
            # Convert to grayscale for better OCR
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Save processed image
            output = io.BytesIO()
            image.save(output, format='PNG')
            return output.getvalue()
            
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return image_content
    
    def extract_health_data(self, image_content: bytes) -> Dict[str, Any]:
        """
        Extract health data from image
        
        Args:
            image_content: Image file content as bytes
            
        Returns:
            Dictionary with extracted health data
        """
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image_content)
            
            # Extract text
            text = self.extract_text_from_image(processed_image)
            
            if not text.strip():
                return {}
            
            # Parse text for health data (reuse PDF processor logic)
            from .pdf import PDFProcessor
            pdf_processor = PDFProcessor()
            extracted_data = pdf_processor._parse_text(text)
            
            return extracted_data
            
        except Exception as e:
            print(f"Error extracting health data from image: {e}")
            return {}

# Global OCR processor instance
ocr_processor = OCRProcessor()
