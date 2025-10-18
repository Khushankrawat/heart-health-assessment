"""
File upload API endpoints
"""

import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import Dict, Any
from core.schema import UploadResponse, HeartDiseaseInput, ErrorResponse
from core.pdf import pdf_processor
from core.ocr import ocr_processor

router = APIRouter(prefix="/api", tags=["upload"])

# Supported file types
SUPPORTED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png"]
SUPPORTED_PDF_TYPE = "application/pdf"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(file: UploadFile) -> bool:
    """Validate uploaded file"""
    # Check file size
    if hasattr(file, 'size') and file.size > MAX_FILE_SIZE:
        return False
    
    # Check file type
    if file.content_type not in SUPPORTED_IMAGE_TYPES + [SUPPORTED_PDF_TYPE]:
        return False
    
    return True

@router.post("/upload", response_model=UploadResponse)
async def upload_health_report(file: UploadFile = File(...)):
    """
    Upload health report (PDF or image) and extract health data
    
    Args:
        file: Uploaded file (PDF, JPG, or PNG)
        
    Returns:
        Upload response with extracted health data
    """
    try:
        # Validate file
        if not validate_file(file):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type or size. Supported: PDF, JPG, PNG (max 10MB)"
            )
        
        # Read file content
        content = await file.read()
        
        # Extract data based on file type
        extracted_data = {}
        confidence = 0.0
        
        if file.content_type == SUPPORTED_PDF_TYPE:
            # Process PDF
            extracted_data = pdf_processor.extract_from_pdf(content)
            confidence = 0.8  # PDF extraction is generally more reliable
        else:
            # Process image
            extracted_data = ocr_processor.extract_health_data(content)
            confidence = 0.6  # OCR is less reliable than PDF parsing
        
        if not extracted_data:
            return UploadResponse(
                success=False,
                message="Could not extract health data from the uploaded file. Please try manual entry.",
                extracted_data=None,
                confidence=0.0
            )
        
        # Map extracted data to schema
        try:
            mapped_data = pdf_processor.map_to_schema(extracted_data)
            
            # Validate mapped data
            heart_disease_input = HeartDiseaseInput(**mapped_data)
            
            return UploadResponse(
                success=True,
                message="Health data extracted successfully. Please review and submit for prediction.",
                extracted_data=heart_disease_input,
                confidence=confidence
            )
            
        except Exception as validation_error:
            return UploadResponse(
                success=False,
                message=f"Extracted data validation failed: {str(validation_error)}. Please try manual entry.",
                extracted_data=None,
                confidence=confidence
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

@router.post("/upload-image", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    Upload image file specifically for OCR processing
    
    Args:
        file: Uploaded image file (JPG or PNG)
        
    Returns:
        Upload response with extracted health data
    """
    try:
        # Validate file type
        if file.content_type not in SUPPORTED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Invalid image type. Supported: JPG, PNG"
            )
        
        # Validate file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size: 10MB"
            )
        
        # Extract data using OCR
        extracted_data = ocr_processor.extract_health_data(content)
        
        if not extracted_data:
            return UploadResponse(
                success=False,
                message="Could not extract text from the uploaded image. Please try manual entry.",
                extracted_data=None,
                confidence=0.0
            )
        
        # Map extracted data to schema
        try:
            mapped_data = pdf_processor.map_to_schema(extracted_data)
            heart_disease_input = HeartDiseaseInput(**mapped_data)
            
            return UploadResponse(
                success=True,
                message="Health data extracted from image successfully. Please review and submit.",
                extracted_data=heart_disease_input,
                confidence=0.6
            )
            
        except Exception as validation_error:
            return UploadResponse(
                success=False,
                message=f"Extracted data validation failed: {str(validation_error)}. Please try manual entry.",
                extracted_data=None,
                confidence=0.6
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats"""
    return {
        "supported_formats": {
            "pdf": "application/pdf",
            "images": SUPPORTED_IMAGE_TYPES
        },
        "max_file_size": "10MB",
        "description": "Upload health reports in PDF format or images (JPG/PNG) for automatic data extraction"
    }
