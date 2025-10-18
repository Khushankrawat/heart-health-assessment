"""
File upload API endpoints
"""

import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request
from typing import Dict, Any
from core.schema import UploadResponse, HeartDiseaseInput, ErrorResponse
from core.pdf import pdf_processor
from core.ocr import ocr_processor
from core.security import security_middleware, log_security_event, get_client_ip

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

async def security_check(request: Request):
    """Security middleware for upload endpoints"""
    await security_middleware.rate_limit_check(request)

@router.post("/upload", response_model=UploadResponse)
async def upload_health_report(
    file: UploadFile = File(...),
    request: Request = None,
    _: None = Depends(security_check)
):
    """
    Upload health report (PDF or image) and extract health data
    
    Args:
        file: Uploaded file (PDF, JPG, or PNG)
        request: FastAPI request object for security logging
        
    Returns:
        Upload response with extracted health data
    """
    try:
        # Basic file validation
        if not validate_file(file):
            log_security_event("invalid_file_upload", {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": getattr(file, 'size', 'unknown')
            }, request)
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type or size. Supported: PDF, JPG, PNG (max 10MB)"
            )
        
        # Read file content
        content = await file.read()
        
        # Enhanced security validation
        security_validation = security_middleware.validate_uploaded_file(
            file.filename or "unknown",
            file.content_type or "unknown",
            len(content),
            content
        )
        
        if not security_validation["is_valid"]:
            log_security_event("security_validation_failed", {
                "filename": file.filename,
                "errors": security_validation["errors"],
                "warnings": security_validation["warnings"]
            }, request)
            raise HTTPException(
                status_code=400,
                detail=f"File security validation failed: {', '.join(security_validation['errors'])}"
            )
        
        # Log warnings if any
        if security_validation["warnings"]:
            log_security_event("file_security_warnings", {
                "filename": file.filename,
                "warnings": security_validation["warnings"]
            }, request)
        
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
async def upload_image(
    file: UploadFile = File(...),
    request: Request = None,
    _: None = Depends(security_check)
):
    """
    Upload image file specifically for OCR processing
    
    Args:
        file: Uploaded image file (JPG or PNG)
        request: FastAPI request object for security logging
        
    Returns:
        Upload response with extracted health data
    """
    try:
        # Validate file type
        if file.content_type not in SUPPORTED_IMAGE_TYPES:
            log_security_event("invalid_image_upload", {
                "filename": file.filename,
                "content_type": file.content_type
            }, request)
            raise HTTPException(
                status_code=400,
                detail="Invalid image type. Supported: JPG, PNG"
            )
        
        # Validate file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            log_security_event("file_too_large", {
                "filename": file.filename,
                "size": len(content),
                "max_size": MAX_FILE_SIZE
            }, request)
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size: 10MB"
            )
        
        # Enhanced security validation
        security_validation = security_middleware.validate_uploaded_file(
            file.filename or "unknown",
            file.content_type or "unknown",
            len(content),
            content
        )
        
        if not security_validation["is_valid"]:
            log_security_event("image_security_validation_failed", {
                "filename": file.filename,
                "errors": security_validation["errors"]
            }, request)
            raise HTTPException(
                status_code=400,
                detail=f"Image security validation failed: {', '.join(security_validation['errors'])}"
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
