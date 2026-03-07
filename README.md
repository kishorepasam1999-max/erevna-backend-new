# Erevna Games Backend

## Overview
Flask REST API backend for Erevna Games platform with authentication, games, surveys, and analytics.

## Tech Stack
- **Backend**: Flask with Flask-RESTX
- **Database**: PostgreSQL (Neon)
- **Authentication**: JWT with bcrypt
- **Email**: Flask-Mail
- **Deployment**: Render

## Environment Variables
Set these in your Render dashboard:

```bash
NEON_DATABASE_URL=postgresql://username:password@ep-xxx-xxx.us-east-1.aws.neon.tech/erevna?sslmode=require
JWT_SECRET_KEY=your-secret-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
OPENROUTER_API_KEY=your-openrouter-key
```

## API Endpoints

### Authentication
- `POST /auth/signin` - User login
- `POST /auth/signup` - User registration
- `POST /auth/verify-otp` - OTP verification

### Games
- `GET /games` - List all games
- `POST /games` - Create new game
- `GET /game-questions` - Get game questions
- `POST /game-moves` - Submit game moves

### Users & Management
- `GET /users` - User management
- `GET /employees` - Employee data
- `GET /clients` - Client management
- `GET /departments` - Department data

### Analytics
- `GET /ai-analytics` - AI-powered analytics
- `GET /client-report` - Client reports
- `GET /surveys` - Survey data
- `GET /responses` - Survey responses

## Database Setup
Uses Neon PostgreSQL. The database schema is auto-created on first deployment.

## Deployment on Render
1. Connect this repository to Render
2. Set environment variables
3. Deploy - Render will automatically install dependencies and start the server

## Local Development
```bash
pip install -r requirements.txt
python app.py
```

API will be available at `http://localhost:5000`
Swagger docs at `http://localhost:5000/swagger`
