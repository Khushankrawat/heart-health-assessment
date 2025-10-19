# Vercel Deployment Guide

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be pushed to GitHub
3. **Model Files**: Ensure your trained model files are in `backend/models/`

## Deployment Steps

### 1. Connect Repository to Vercel

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Vercel will automatically detect the `vercel.json` configuration

### 2. Environment Variables

Set these environment variables in your Vercel project settings:

```bash
# Security
SECRET_KEY=your-super-secure-secret-key-here

# CORS (replace with your Vercel domain)
CORS_ORIGINS=https://your-project-name.vercel.app

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Environment
ENVIRONMENT=production
DEBUG=false

# File Upload
MAX_FILE_SIZE=10485760
PLATFORM_MAX_SIZE=52428800

# Logging
LOG_LEVEL=WARNING
```

### 3. Model Files Setup

**Important**: Vercel has file size limitations. You need to:

1. **Train your model locally**:
   ```bash
   python scripts/train.py
   ```

2. **Commit model files** to your repository:
   ```bash
   git add backend/models/
   git commit -m "Add trained model files"
   git push origin main
   ```

3. **Ensure model files are under 50MB total** (Vercel limit)

### 4. Deploy

1. **Automatic Deployment**: Vercel will deploy automatically when you push to main
2. **Manual Deployment**: Click "Deploy" in the Vercel dashboard

### 5. Verify Deployment

1. **Backend API**: `https://your-project-name.vercel.app/api/health`
2. **Frontend**: `https://your-project-name.vercel.app/`
3. **API Docs**: `https://your-project-name.vercel.app/docs`

## Troubleshooting

### Common Issues

#### 1. **Function Payload Too Large**
- **Error**: `FUNCTION_PAYLOAD_TOO_LARGE`
- **Solution**: Reduce model file sizes or use lighter ML libraries

#### 2. **Build Failures**
- **Error**: Python package installation fails
- **Solution**: Check `requirements-vercel.txt` for compatibility

#### 3. **CORS Errors**
- **Error**: Frontend can't connect to API
- **Solution**: Update `CORS_ORIGINS` with your Vercel domain

#### 4. **Model Loading Issues**
- **Error**: Model files not found
- **Solution**: Ensure model files are committed to repository

### Performance Optimization

1. **Use `requirements-vercel.txt`** for lighter dependencies
2. **Optimize model files** (use joblib compression)
3. **Enable caching** for static assets
4. **Use CDN** for better performance

## File Structure for Vercel

```
your-project/
├── vercel.json              # Vercel configuration
├── .vercelignore           # Files to exclude
├── backend/
│   ├── app.py              # FastAPI app
│   ├── requirements-vercel.txt  # Lightweight requirements
│   ├── models/             # Trained model files
│   └── core/               # Core modules
├── frontend/
│   ├── package.json        # Frontend dependencies
│   ├── vite.config.ts      # Vite configuration
│   └── src/                # React source code
└── README.md
```

## Limitations

- **Function timeout**: 30 seconds max
- **Payload size**: 50MB max
- **Cold starts**: First request may be slower
- **Heavy ML libraries**: May not work due to size constraints

## Alternative Approach

If Vercel limitations are too restrictive, consider:

1. **Separate deployments**:
   - Frontend on Vercel
   - Backend on Railway/Render/Heroku

2. **Use lighter ML libraries**:
   - Replace XGBoost with lighter alternatives
   - Use pre-trained models from cloud services

3. **Hybrid approach**:
   - Keep core logic on Vercel
   - Use external ML services for heavy computations
