"""
Heart Disease Risk Predictor - FastAPI Application
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import predict, upload
from core.model import model_instance
from core.preprocess import preprocessor_instance
from core.security import SecurityConfig, log_security_event

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting Heart Disease Risk Predictor API...")
    
    # Load model
    model_path = "models"
    if not model_instance.load_model():
        print("Warning: Model could not be loaded. API will not function properly.")
    
    # Load preprocessor metadata
    meta_path = os.path.join(model_path, "feature_meta.json")
    if os.path.exists(meta_path):
        preprocessor_instance.load_feature_meta(meta_path)
        print("Preprocessor metadata loaded successfully.")
    else:
        print("Warning: Preprocessor metadata not found.")
    
    print("API startup complete.")
    
    yield
    
    # Shutdown
    print("Shutting down Heart Disease Risk Predictor API...")

# Initialize security configuration
security_config = SecurityConfig()

# Create FastAPI app
app = FastAPI(
    title="Heart Disease Risk Predictor",
    description="AI-powered heart disease risk prediction using machine learning",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS with environment-based settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=security_config.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predict.router)
app.include_router(upload.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Heart Disease Risk Predictor API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "predict": "/api/predict",
            "upload": "/api/upload",
            "health": "/api/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_loaded = model_instance.model is not None
    preprocessor_loaded = preprocessor_instance.feature_meta is not None
    
    return {
        "status": "healthy" if model_loaded and preprocessor_loaded else "degraded",
        "model_loaded": model_loaded,
        "preprocessor_loaded": preprocessor_loaded,
        "version": "1.0.0"
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc):
    """General exception handler"""
    # Log security events for unexpected errors
    log_security_event("unexpected_error", {
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "path": str(request.url.path),
        "method": request.method
    }, request)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if security_config.debug else "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=security_config.api_host, 
        port=security_config.api_port,
        log_level=security_config.log_level.lower()
    )
