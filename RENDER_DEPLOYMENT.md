# Render.com Deployment Guide

## 🚀 Deploy Heart Disease Prediction App on Render.com

### Prerequisites
- GitHub repository with your code
- Render.com account (free tier available)

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Connect your GitHub repository

### Step 2: Deploy Backend API
1. **Create New Web Service**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select the repository: `heart-health-assessment`

2. **Configure Backend Service**
   ```
   Name: heart-disease-backend
   Environment: Python 3
   Build Command: cd backend && pip install -r requirements.txt
   Start Command: cd backend && python app.py
   ```

3. **Environment Variables**
   ```
   PYTHON_VERSION=3.9.18
   MAX_FILE_SIZE=10485760
   PLATFORM_MAX_SIZE=209715200
   SECRET_KEY=[Generate random key]
   CORS_ORIGINS=https://heart-disease-frontend.onrender.com
   ENVIRONMENT=production
   DEBUG=false
   API_HOST=0.0.0.0
   API_PORT=10000
   ```

### Step 3: Deploy Frontend
1. **Create New Static Site**
   - Click "New" → "Static Site"
   - Connect your GitHub repository

2. **Configure Frontend Service**
   ```
   Name: heart-disease-frontend
   Build Command: cd frontend && npm ci --only=production && npm run build
   Publish Directory: frontend/dist
   ```

3. **Environment Variables**
   ```
   NODE_VERSION=18.17.0
   VITE_API_URL=https://heart-disease-backend.onrender.com/api
   ```

### Step 4: Update CORS Settings
After both services are deployed, update the backend CORS_ORIGINS with your actual frontend URL.

### Step 5: Test Deployment
1. Visit your frontend URL
2. Test the prediction functionality
3. Test file upload (should work without 300MB errors!)

## 🎯 Benefits of Render.com
- ✅ **No file size limits** like Vercel's 300MB restriction
- ✅ **Better for Python apps** with proper Python runtime
- ✅ **Free tier available** with generous limits
- ✅ **Automatic deployments** from GitHub
- ✅ **Built-in health checks** and monitoring

## 📊 Expected Performance
- **Cold start**: 2-3 seconds
- **File upload**: No size restrictions (within reason)
- **API response**: Fast with proper caching
- **Uptime**: 99.9% on paid plans

## 🔧 Troubleshooting
- **Build fails**: Check Python/Node versions
- **CORS errors**: Update CORS_ORIGINS with correct URLs
- **File upload fails**: Check MAX_FILE_SIZE setting
- **API not responding**: Check health endpoint

## 🌐 URLs After Deployment
- **Frontend**: `https://heart-disease-frontend.onrender.com`
- **Backend API**: `https://heart-disease-backend.onrender.com`
- **Health Check**: `https://heart-disease-backend.onrender.com/health`
