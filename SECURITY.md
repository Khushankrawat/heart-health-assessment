# Security Configuration Guide

## 🔒 Production Security Setup

### 1. Environment Variables

Create a `.env` file in your project root with the following variables:

```bash
# Copy from env.example and update for production
cp env.example .env
```

### 2. Required Security Settings

#### **Critical Security Variables**
```bash
# Application Environment
ENVIRONMENT=production
DEBUG=false

# Security Configuration
SECRET_KEY=your-super-secure-secret-key-here-change-this
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# File Upload Security
MAX_FILE_SIZE=10485760
ENABLE_FILE_SCANNING=true

# Rate Limiting
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_WINDOW=3600

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/heart-health-assessment/app.log
```

### 3. Security Features Implemented

#### **✅ File Security**
- **File type validation** - Only PDF, JPG, PNG allowed
- **File size limits** - Maximum 10MB per file
- **Magic byte validation** - Verifies file headers match extensions
- **Content scanning** - Detects suspicious patterns in uploaded files
- **Security logging** - All file uploads logged for monitoring

#### **✅ Rate Limiting**
- **Per-IP rate limiting** - Configurable requests per time window
- **Endpoint-specific limits** - Different limits for different endpoints
- **Graceful degradation** - Returns proper HTTP 429 responses
- **Rate limit headers** - Includes remaining requests and reset time

#### **✅ Input Sanitization**
- **String sanitization** - Removes control characters and limits length
- **Numeric validation** - Ensures values are within expected ranges
- **Boolean sanitization** - Properly handles boolean inputs
- **Nested data sanitization** - Recursively sanitizes complex objects

#### **✅ CORS Protection**
- **Environment-based origins** - Configured via environment variables
- **Method restrictions** - Only GET and POST allowed
- **Credential handling** - Properly configured for authentication

#### **✅ Security Logging**
- **Comprehensive logging** - All security events logged
- **Structured logging** - JSON format for easy parsing
- **Client IP tracking** - Includes forwarded headers
- **Request context** - User agent, path, method logged

### 4. Production Deployment Checklist

#### **Before Deployment:**
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Generate secure `SECRET_KEY`
- [ ] Configure production `CORS_ORIGINS`
- [ ] Set up log file directory with proper permissions
- [ ] Configure rate limiting for expected traffic
- [ ] Enable file scanning if needed

#### **Security Monitoring:**
- [ ] Monitor log files for security events
- [ ] Set up alerts for rate limit violations
- [ ] Monitor file upload patterns
- [ ] Track failed validation attempts

### 5. Security Headers (Optional)

Add these headers to your reverse proxy (nginx/Apache):

```nginx
# Security Headers
add_header X-Content-Type-Options nosniff;
add_header X-Frame-Options DENY;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
add_header Content-Security-Policy "default-src 'self'";
```

### 6. Monitoring and Alerts

#### **Key Metrics to Monitor:**
- Rate limit violations per IP
- File upload security warnings
- Input validation failures
- Unexpected errors and exceptions

#### **Alert Thresholds:**
- More than 10 rate limit violations per hour from single IP
- More than 5 security warnings per hour
- More than 20 validation failures per hour

### 7. Backup and Recovery

#### **Security Configuration Backup:**
- Store `.env` file securely (not in version control)
- Document all security settings
- Test configuration changes in staging environment

### 8. Regular Security Maintenance

#### **Monthly Tasks:**
- Review security logs for patterns
- Update rate limiting based on traffic patterns
- Rotate secret keys if compromised
- Review and update CORS origins

#### **Quarterly Tasks:**
- Security audit of configuration
- Review and update file validation rules
- Test security features and incident response

## 🚨 Security Incident Response

### If Security Breach Detected:

1. **Immediate Response:**
   - Block suspicious IP addresses
   - Increase rate limiting temporarily
   - Review security logs for scope

2. **Investigation:**
   - Analyze attack patterns
   - Check for data exposure
   - Document findings

3. **Recovery:**
   - Patch vulnerabilities
   - Update security configuration
   - Monitor for continued attacks

## 📞 Security Contact

For security issues or questions:
- Review security logs first
- Check configuration against this guide
- Test changes in staging environment
- Document all security-related changes
