# 🚀 Banta Deployment Guide
## Deploy Frontend on Vercel + Backend on Render

### 📋 Overview
- **Frontend**: React + Vite → Vercel
- **Backend**: FastAPI → Render  
- **Database**: AWS S3 for file storage

---

## 🔧 Step 1: Deploy Backend on Render

### 1.1 Push Backend to GitHub
```bash
# Navigate to your project
cd "C:\Users\canta\Desktop\VDS - new"

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: Banta API"

# Create GitHub repo and push
git remote add origin https://github.com/yourusername/banta-api.git
git push -u origin main
```

### 1.2 Create Render Web Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Configure:
   ```
   Name: banta-api
   Region: Oregon (US West)
   Branch: main
   Root Directory: src
   Runtime: Python 3
   Build Command: pip install -r requirements-prod.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

### 1.3 Set Environment Variables in Render
```bash
# Required
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your_s3_bucket_name

# Optional
ENVIRONMENT=production
DEBUG=False
FRONTEND_URL=https://your-vercel-app.vercel.app
```

### 1.4 Deploy & Note Your API URL
After deployment, note your Render URL:
```
https://banta-api-xyz123.onrender.com
```

---

## 🎨 Step 2: Deploy Frontend on Vercel

### 2.1 Update API URL in Frontend
In `frontend/src/utils/api.js`, update line 16:
```javascript
return 'https://YOUR-RENDER-APP-NAME.onrender.com'
```

### 2.2 Push Frontend to GitHub
```bash
# Navigate to frontend
cd frontend

# Initialize git (if separate repo)
git init
git add .
git commit -m "Initial commit: Banta Frontend"
git remote add origin https://github.com/yourusername/banta-frontend.git
git push -u origin main
```

### 2.3 Deploy on Vercel

#### Option A: Vercel Dashboard
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"New Project"**
3. Import your GitHub repo
4. Configure:
   ```
   Framework Preset: Vite
   Root Directory: frontend (if monorepo) or leave empty
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

#### Option B: Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from frontend directory
cd frontend
vercel

# Follow the prompts:
# Set up and deploy? [Y/n] Y
# Which scope? Select your account
# Link to existing project? [y/N] N  
# What's your project's name? banta-dashboard
# In which directory is your code located? ./
```

### 2.4 Set Environment Variables in Vercel
In Vercel Dashboard → Your Project → Settings → Environment Variables:
```bash
VITE_API_BASE_URL=https://your-render-app-name.onrender.com
VITE_API_TIMEOUT=30000
VITE_APP_NAME=Banta
VITE_ENVIRONMENT=production
```

---

## 🔗 Step 3: Connect Frontend & Backend

### 3.1 Update Backend CORS
In your Render dashboard, update environment variables:
```bash
# Add your Vercel URL
FRONTEND_URL=https://your-vercel-app.vercel.app
VERCEL_URL=your-vercel-app.vercel.app
```

### 3.2 Redeploy Backend
After updating environment variables, trigger a new deployment in Render.

### 3.3 Test Connection
1. Visit your Vercel app: `https://your-app.vercel.app`
2. Try uploading a CSV file
3. Check browser console for any CORS errors
4. Verify API calls in Network tab

---

## 🧪 Step 4: Testing & Verification

### 4.1 Test Endpoints
- **API Health**: `https://your-render-app.onrender.com/health`
- **API Docs**: `https://your-render-app.onrender.com/docs`
- **Frontend**: `https://your-vercel-app.vercel.app`

### 4.2 Common Issues & Solutions

#### CORS Errors
```javascript
// Update backend CORS origins in src/main.py line 55-56
"https://your-actual-vercel-app.vercel.app",
```

#### API Connection Issues
```javascript
// Check frontend API URL in src/utils/api.js line 16
return 'https://your-actual-render-app.onrender.com'
```

#### Environment Variables Not Loading
- Ensure variables are prefixed with `VITE_` in frontend
- Redeploy after adding new environment variables

---

## 📱 Step 5: Custom Domain (Optional)

### 5.1 Vercel Custom Domain
1. Vercel Dashboard → Your Project → Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

### 5.2 Update Backend CORS
Add your custom domain to backend environment variables:
```bash
CUSTOM_DOMAIN=https://yourdomain.com
```

---

## 🔄 Step 6: Continuous Deployment

### 6.1 Auto-Deploy Setup
Both Vercel and Render auto-deploy when you push to `main` branch:

```bash
# Make changes
git add .
git commit -m "Update: your changes"
git push

# Vercel redeploys automatically
# Render redeploys automatically
```

---

## 📊 Final URLs

After deployment, you'll have:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-api.onrender.com`
- **API Docs**: `https://your-api.onrender.com/docs`

---

## 🆘 Troubleshooting

### Build Failures
- Check build logs in Vercel/Render dashboards
- Verify all dependencies are in package.json/requirements.txt
- Ensure environment variables are set correctly

### Performance Issues
- Render free tier spins down after 15min inactivity
- First request after sleep takes 30+ seconds (cold start)
- Consider upgrading to paid tier for production

### CORS Issues
- Check browser console for exact error messages
- Verify frontend URL is added to backend CORS origins
- Ensure HTTPS is used in production URLs

---

🎉 **Your Banta application is now live!**
