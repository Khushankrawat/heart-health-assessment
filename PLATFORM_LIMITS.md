# Platform Limitations and File Upload Issues

## The 300MB Error Issue

If you're seeing the error "Size of uploaded file exceeds 300MB", this is **not** coming from your application code. Here's what's happening:

### Root Cause
- **Your application correctly limits files to 10MB** (configured in multiple places)
- **Vercel has a hard platform limit of ~250MB** for function payloads
- **The 300MB error indicates you're hitting Vercel's platform limit**, not your app's 10MB limit

### Platform Limits by Deployment Platform

| Platform | Function Size Limit | Payload Limit | Notes |
|----------|-------------------|---------------|-------|
| **Vercel** | 250MB | ~250MB | Hard limit, cannot be increased |
| **Netlify** | 50MB | ~50MB | Can be increased with Pro plan |
| **Railway** | 1GB | ~1GB | More generous limits |
| **Heroku** | 500MB | ~500MB | Depends on dyno type |

### Solutions Implemented

#### 1. Enhanced Error Handling
- Added platform-specific size validation (200MB threshold)
- Better error messages distinguishing app vs platform limits
- Proper HTTP status codes (413 for payload too large)

#### 2. Frontend Improvements
- Better file rejection handling with specific error messages
- Client-side validation before upload attempts
- Clear user feedback for different error types

#### 3. Configuration Options
- `MAX_FILE_SIZE`: Application-level limit (default: 10MB)
- `PLATFORM_MAX_SIZE`: Platform-specific limit (default: 200MB)
- Configurable via environment variables

### Recommended Actions

#### For Development
1. **Keep your 10MB limit** - it's appropriate for medical documents
2. **Test with files under 10MB** to avoid platform issues
3. **Use the enhanced error messages** to debug upload issues

#### For Production
1. **Consider alternative platforms** if you need larger file support:
   - Railway (1GB limit)
   - AWS Lambda (6MB request, 512MB response)
   - Google Cloud Functions (32MB request)
   - Azure Functions (100MB request)

2. **Implement file compression** for larger documents
3. **Use cloud storage** (S3, Cloudinary) for file uploads with direct processing

### Environment Variables

```bash
# Application file size limit (10MB)
MAX_FILE_SIZE=10485760

# Platform-specific limit (200MB for Vercel)
PLATFORM_MAX_SIZE=209715200
```

### Testing the Fix

1. **Small files (< 10MB)**: Should work normally
2. **Medium files (10-200MB)**: Should show platform limit error
3. **Large files (> 200MB)**: Should be caught by platform before reaching your app

### Alternative Solutions

If you need to support larger files:

#### Option 1: Chunked Upload
```python
# Implement chunked file upload
# Split large files into smaller chunks
# Reassemble on the server
```

#### Option 2: Direct Cloud Storage
```python
# Upload directly to S3/Cloudinary
# Process files asynchronously
# Return processing status to client
```

#### Option 3: Platform Migration
- Move to Railway or AWS for higher limits
- Use serverless functions with larger payload support
- Implement proper file streaming

### Monitoring

The application now logs platform limit violations:
- `file_near_platform_limit`: When files exceed platform thresholds
- `invalid_file_upload`: When files exceed application limits
- Security events are logged for analysis

### Conclusion

The 300MB error is a **platform limitation**, not a bug in your application. The implemented solutions provide:
- Better error handling and user feedback
- Clear distinction between app and platform limits
- Configurable thresholds for different deployment environments
- Proper logging for monitoring and debugging

For medical document processing, the 10MB limit should be sufficient for most use cases.
