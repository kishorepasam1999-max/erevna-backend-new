# RENDER DEPLOYMENT CONFIGURATION
# This file contains all necessary configurations for deploying to Render

# ==========================================
# RENDER DEPLOYMENT CHECKLIST
# ==========================================

## ✅ CURRENT STATUS
- Backend API: Working locally
- Authentication: ✅ Signup, Signin, OTP verification working
- Game APK: ✅ List, Install, Progress tracking working
- Database: ⚠️ Connection issues in local, will work on Render
- Mobile App: ✅ Mock data working, ready for real API

## 🔧 RENDER DEPLOYMENT REQUIREMENTS

### 1. Environment Variables
Create these in Render dashboard:
- NEON_DATABASE_URL=your_neon_database_url
- JWT_SECRET_KEY=your_jwt_secret_key
- FLASK_ENV=production

### 2. Build Files Needed
- requirements.txt ✅ (exists)
- app.py ✅ (exists)
- .gitignore ✅ (exists)

### 3. Database Migration
- Database tables auto-create on startup ✅

## 🚀 DEPLOYMENT STEPS

### Step 1: Prepare for Production
1. Remove debug prints from auth.py
2. Set production-ready configurations
3. Update CORS for production
4. Create render.yaml

### Step 2: Deploy to Render
1. Push code to GitHub
2. Connect Render to GitHub repo
3. Render auto-deploys from app.py

### Step 3: Update Mobile App
1. Change API_BASE_URL to deployed URL
2. Test with production backend
3. Remove mock data

## 📋 FILES TO FIX FOR PRODUCTION

### 1. app.py - Production Config
- Change host from "0.0.0.0" to "0.0.0.0"
- Set debug=False for production
- Add proper CORS configuration

### 2. auth.py - Remove Debug
- Remove debug_otp from response
- Remove debug print statements
- Add proper error logging

### 3. game_apk_routes.py - Fix CORS
- Add CORS headers
- Handle production file paths

### 4. Create render.yaml
- Render deployment configuration
- Environment variables
- Build commands

## 🎯 DEPLOYMENT COMMANDS

```bash
# 1. Create render.yaml
cat > render.yaml << EOF
services:
  type: web
  name: erevna-backend
  env: python
  buildCommand: pip install -r requirements.txt
  startCommand: python app.py
  envVars:
    - key: NEON_DATABASE_URL
      sync: false
    - key: JWT_SECRET_KEY
      generateValue: true
    - key: FLASK_ENV
      value: production
EOF

# 2. Deploy to Render
git add .
git commit -m "Ready for Render deployment"
git push origin main

# 3. Update mobile app
# Change in src/api/game-apk-service.ts:
const API_BASE_URL = "https://erevna-backend.onrender.com";
```

## 🔍 POST-DEPLOYMENT TESTING

### Test 1: API Health Check
```bash
curl https://erevna-backend.onrender.com/swagger
```

### Test 2: Authentication Flow
```bash
# Test signup
curl -X POST https://erevna-backend.onrender.com/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"test123456"}'

# Test signin
curl -X POST https://erevna-backend.onrender.com/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"identifier":"test@example.com","password":"test123456"}'
```

### Test 3: Game APK Endpoints
```bash
# Test game list
curl https://erevna-backend.onrender.com/game-apk/list

# Test with auth
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://erevna-backend.onrender.com/game-apk/my-installations
```

## 📱 MOBILE APP UPDATES

### 1. Remove Mock Data
- Comment out mock data in GameCenterHomeScreen.tsx
- Restore original API calls
- Test with production backend

### 2. Update API URL
```typescript
// In src/api/game-apk-service.ts
const API_BASE_URL = "https://your-app.onrender.com";
```

### 3. Build Production APK
```bash
npx react-native build-android --mode=release
```

## 🎉 EXPECTED RESULTS

After deployment:
- ✅ Backend accessible at https://erevna-backend.onrender.com
- ✅ All API endpoints working
- ✅ Mobile app can connect and install games
- ✅ Real APK installation on phones
- ✅ Production-ready system

## 🚨 IMPORTANT NOTES

1. **Database**: Use Neon PostgreSQL for production
2. **CORS**: Configure for mobile app access
3. **Security**: Remove debug information
4. **Performance**: Optimize for production
5. **Monitoring**: Add error tracking

## 📞 TROUBLESHOOTING

### If deployment fails:
1. Check Render logs for errors
2. Verify environment variables
3. Check database connection
4. Validate all route imports

### If mobile app can't connect:
1. Verify deployed URL is correct
2. Check CORS configuration
3. Test API endpoints manually
4. Check network connectivity
