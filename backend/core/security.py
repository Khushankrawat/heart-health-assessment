"""
Security utilities and middleware for the Heart Health Assessment API
"""

import os
import re
import hashlib
import time
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.getenv("LOG_FILE", "logs/app.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SecurityConfig:
    """Security configuration management"""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.secret_key = os.getenv("SECRET_KEY", "default-secret-key")
        self.cors_origins = self._parse_cors_origins()
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "10485760"))
        self.allowed_file_types = os.getenv("ALLOWED_FILE_TYPES", "").split(",")
        self.enable_file_scanning = os.getenv("ENABLE_FILE_SCANNING", "false").lower() == "true"
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
    
    def _parse_cors_origins(self) -> List[str]:
        """Parse CORS origins from environment variable"""
        origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]

class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(lambda: deque())
    
    def is_allowed(self, client_ip: str) -> Tuple[bool, Dict[str, int]]:
        """Check if request is allowed for given client IP"""
        now = time.time()
        client_requests = self.requests[client_ip]
        
        # Remove old requests outside the window
        while client_requests and client_requests[0] <= now - self.window_seconds:
            client_requests.popleft()
        
        # Check if under limit
        if len(client_requests) >= self.max_requests:
            return False, {
                "limit": self.max_requests,
                "remaining": 0,
                "reset_time": int(client_requests[0] + self.window_seconds)
            }
        
        # Add current request
        client_requests.append(now)
        
        return True, {
            "limit": self.max_requests,
            "remaining": self.max_requests - len(client_requests),
            "reset_time": int(now + self.window_seconds)
        }

class FileSecurityValidator:
    """File security validation"""
    
    def __init__(self):
        self.allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}
        self.allowed_mime_types = {
            'application/pdf',
            'image/jpeg',
            'image/jpg', 
            'image/png'
        }
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.suspicious_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>'
        ]
    
    def validate_file(self, filename: str, content_type: str, file_size: int, content: bytes) -> Dict[str, any]:
        """Comprehensive file validation"""
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check file size
        if file_size > self.max_file_size:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"File size {file_size} exceeds maximum {self.max_file_size}")
        
        # Check file extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in self.allowed_extensions:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"File extension {file_ext} not allowed")
        
        # Check MIME type
        if content_type not in self.allowed_mime_types:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"MIME type {content_type} not allowed")
        
        # Check for suspicious content (for text-based files)
        if content_type.startswith('text/') or file_ext == '.pdf':
            try:
                content_str = content.decode('utf-8', errors='ignore')
                for pattern in self.suspicious_patterns:
                    if re.search(pattern, content_str, re.IGNORECASE):
                        validation_result["warnings"].append(f"Suspicious pattern detected: {pattern}")
            except Exception as e:
                validation_result["warnings"].append(f"Could not scan content: {str(e)}")
        
        # Check file header/magic bytes
        if not self._validate_file_header(content, file_ext):
            validation_result["warnings"].append("File header does not match extension")
        
        return validation_result
    
    def _validate_file_header(self, content: bytes, file_ext: str) -> bool:
        """Validate file header matches extension"""
        if len(content) < 4:
            return False
        
        magic_bytes = {
            '.pdf': b'%PDF',
            '.jpg': b'\xff\xd8\xff',
            '.jpeg': b'\xff\xd8\xff',
            '.png': b'\x89PNG\r\n\x1a\n'
        }
        
        if file_ext in magic_bytes:
            return content.startswith(magic_bytes[file_ext])
        
        return True

class InputSanitizer:
    """Input sanitization utilities"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            return str(value)
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_numeric(value: any, min_val: float = None, max_val: float = None) -> float:
        """Sanitize numeric input"""
        try:
            num_val = float(value)
            
            if min_val is not None and num_val < min_val:
                num_val = min_val
            if max_val is not None and num_val > max_val:
                num_val = max_val
            
            return num_val
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def sanitize_boolean(value: any) -> bool:
        """Sanitize boolean input"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)

class SecurityMiddleware:
    """Security middleware for FastAPI"""
    
    def __init__(self):
        self.config = SecurityConfig()
        self.rate_limiter = RateLimiter(
            self.config.rate_limit_requests,
            self.config.rate_limit_window
        )
        self.file_validator = FileSecurityValidator()
    
    async def rate_limit_check(self, request: Request) -> None:
        """Check rate limiting"""
        client_ip = request.client.host
        
        # Skip rate limiting for health checks
        if request.url.path in ['/health', '/']:
            return
        
        is_allowed, rate_info = self.rate_limiter.is_allowed(client_ip)
        
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": str(rate_info["reset_time"])
                }
            )
    
    def validate_uploaded_file(self, filename: str, content_type: str, file_size: int, content: bytes) -> Dict[str, any]:
        """Validate uploaded file for security"""
        return self.file_validator.validate_file(filename, content_type, file_size, content)
    
    def sanitize_request_data(self, data: Dict[str, any]) -> Dict[str, any]:
        """Sanitize request data"""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_string(value)
            elif isinstance(value, (int, float)):
                sanitized[key] = InputSanitizer.sanitize_numeric(value)
            elif isinstance(value, bool):
                sanitized[key] = InputSanitizer.sanitize_boolean(value)
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_request_data(value)
            elif isinstance(value, list):
                sanitized[key] = [self.sanitize_request_data(item) if isinstance(item, dict) else item for item in value]
            else:
                sanitized[key] = value
        
        return sanitized

# Global security instance
security_middleware = SecurityMiddleware()

def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    # Check for forwarded headers
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host

def log_security_event(event_type: str, details: Dict[str, any], request: Request = None):
    """Log security events"""
    log_data = {
        "event_type": event_type,
        "timestamp": time.time(),
        "details": details
    }
    
    if request:
        log_data["client_ip"] = get_client_ip(request)
        log_data["user_agent"] = request.headers.get("User-Agent", "")
        log_data["path"] = str(request.url.path)
        log_data["method"] = request.method
    
    logger.warning(f"Security Event: {log_data}")
