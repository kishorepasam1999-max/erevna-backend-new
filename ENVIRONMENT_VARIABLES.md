# 🔐 RENDER ENVIRONMENT VARIABLES

## 📋 REQUIRED ENVIRONMENT VARIABLES

Add these in your Render dashboard:

### 1. NEON_DATABASE_URL
```
NEON_DATABASE_URL=postgresql://your_username:your_password@ep-xxx-xxx.us-east-1.aws.neon.tech/erevna?sslmode=require&channel_binding=require
```

**How to get this:**
- Go to neon.tech
- Your database dashboard → Connection string
- Copy the full connection string

### 2. JWT_SECRET_KEY
```
JWT_SECRET_KEY=your_super_secret_key_here_at_least_32_characters_long
```

**How to generate:**
```bash
# Generate secure random key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. FLASK_ENV
```
FLASK_ENV=production
```

### 4. HOST
```
HOST=0.0.0.0
```

### 5. PORT
```
PORT=5000
```

## 📧 OPTIONAL ENVIRONMENT VARIABLES

### For Email Services (if needed)
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=your_email@gmail.com
```

## 🚀 RENDER SETUP STEPS

### Step 1: Create Render Service
1. Go to [render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Use "render.yaml" configuration
5. Add environment variables above

### Step 2: Configure Environment Variables
In Render dashboard → Environment tab:
1. **NEON_DATABASE_URL** - Paste your Neon connection string
2. **JWT_SECRET_KEY** - Generate or create secure key
3. **FLASK_ENV** - Set to "production"
4. **HOST** - Set to "0.0.0.0"
5. **PORT** - Set to "5000"

### Step 3: Deploy
- Click "Create Web Service"
- Render will automatically build and deploy
- Wait for deployment to complete

## 🔍 VERIFICATION

After deployment, test:
```bash
# Test health
curl https://your-app-name.onrender.com/swagger

# Test API
curl https://your-app-name.onrender.com/game-apk/list
```

## 📱 MOBILE APP UPDATE

After deployment, update your mobile app:

### In src/api/game-apk-service.ts:
```typescript
// Change this line:
const API_BASE_URL = "https://your-app-name.onrender.com";
```

## ⚠️ IMPORTANT NOTES

1. **Security**: Never commit environment variables to Git
2. **Database**: Use Neon PostgreSQL for production (not SQLite)
3. **URL**: Your app will be available at `https://your-app-name.onrender.com`
4. **Testing**: Always test with real deployed URL
