# Cloud Deployment Guide - ResuMAX

## Overview
This guide covers deploying ResuMAX to production cloud environments.

## Deployment Options

### Option 1: Google Cloud Platform (Recommended)

#### Backend - Cloud Run
```bash
# 1. Build and deploy backend
cd backend
gcloud run deploy resumax-backend \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production

# 2. Set secrets
gcloud secrets create firebase-credentials --data-file=secrets/firebase-credentials.json
gcloud secrets create openai-api-key --data-file=<(echo -n "$OPENAI_API_KEY")

# 3. Grant Cloud Run access to secrets
gcloud run services update resumax-backend \
  --update-secrets=FIREBASE_CREDENTIALS=/secrets/firebase-credentials:latest \
  --update-secrets=OPENAI_API_KEY=/secrets/openai-api-key:latest
```

#### Frontend - Firebase Hosting
```bash
# 1. Install Firebase CLI
npm install -g firebase-tools

# 2. Login and initialize
firebase login
firebase init hosting

# 3. Build and deploy
cd frontend
npm run build
firebase deploy --only hosting
```

#### Database - Cloud SQL (PostgreSQL)
```bash
# 1. Create database
gcloud sql instances create resumax-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# 2. Create database
gcloud sql databases create resumax --instance=resumax-db

# 3. Create user
gcloud sql users create resumax \
  --instance=resumax-db \
  --password=<secure-password>

# 4. Update backend environment
export DATABASE_URL="postgresql://resumax:<password>@/<db>?host=/cloudsql/<project>:<region>:resumax-db"
```

---

### Option 2: AWS

#### Backend - Elastic Beanstalk
```bash
# 1. Install EB CLI
pip install awsebcli

# 2. Initialize
cd backend
eb init -p python-3.11 resumax --region us-east-1

# 3. Create environment
eb create resumax-prod

# 4. Set environment variables
eb setenv \
  ENVIRONMENT=production \
  FIREBASE_CREDENTIALS_PATH=/etc/secrets/firebase.json \
  OPENAI_API_KEY=$OPENAI_API_KEY

# 5. Deploy
eb deploy
```

#### Frontend - S3 + CloudFront
```bash
# 1. Build frontend
cd frontend
npm run build

# 2. Create S3 bucket
aws s3 mb s3://resumax-frontend

# 3. Enable static website hosting
aws s3 website s3://resumax-frontend \
  --index-document index.html

# 4. Upload build
aws s3 sync dist/ s3://resumax-frontend

# 5. Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name resumax-frontend.s3.amazonaws.com
```

#### Database - RDS PostgreSQL
```bash
aws rds create-db-instance \
  --db-instance-identifier resumax-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username resumax \
  --master-user-password <secure-password> \
  --allocated-storage 20
```

---

### Option 3: Vercel + Railway (Easiest)

#### Frontend - Vercel
```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy
cd frontend
vercel --prod

# 3. Set environment variables in Vercel dashboard
# VITE_API_URL
# VITE_FIREBASE_*
```

#### Backend - Railway
```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
cd backend
railway init

# 4. Link to project
railway link

# 5. Add PostgreSQL
railway add --plugin postgresql

# 6. Set environment variables
railway vars set \
  OPENAI_API_KEY=$OPENAI_API_KEY \
  FIREBASE_PROJECT_ID=resumax-1f61f

# 7. Deploy
railway up
```

---

### Option 4: Docker + DigitalOcean/Linode

#### Build and Push Images
```bash
# 1. Build images
docker build -t resumax-backend:latest ./backend
docker build -t resumax-frontend:latest ./frontend

# 2. Tag for registry
docker tag resumax-backend:latest registry.digitalocean.com/resumax/backend:latest
docker tag resumax-frontend:latest registry.digitalocean.com/resumax/frontend:latest

# 3. Push to registry
docker push registry.digitalocean.com/resumax/backend:latest
docker push registry.digitalocean.com/resumax/frontend:latest
```

#### Deploy with Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    image: registry.digitalocean.com/resumax/backend:latest
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
    ports:
      - "8000:8000"
    restart: always

  frontend:
    image: registry.digitalocean.com/resumax/frontend:latest
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: always

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=resumax
      - POSTGRES_USER=resumax
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

volumes:
  postgres_data:
```

---

## Production Environment Variables

### Backend
```bash
# Required
ENVIRONMENT=production
FIREBASE_PROJECT_ID=resumax-1f61f
FIREBASE_CREDENTIALS_PATH=/etc/secrets/firebase.json
OPENAI_API_KEY=sk-proj-...
DATABASE_URL=postgresql://user:pass@host:5432/resumax

# Optional
SECRET_KEY=<generate-random-32-char-key>
CORS_ORIGINS=["https://resumax.app"]
SENTRY_DSN=https://...
```

### Frontend
```bash
VITE_API_URL=https://api.resumax.app
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=...
VITE_FIREBASE_PROJECT_ID=resumax-1f61f
VITE_FIREBASE_STORAGE_BUCKET=...
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=...
```

---

## Pre-Deployment Checklist

### Security
- [ ] Generate new SECRET_KEY for production
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS for production domain only
- [ ] Enable Firebase App Check
- [ ] Set up rate limiting
- [ ] Configure CSP headers

### Performance
- [ ] Enable gzip compression
- [ ] Configure CDN for static assets
- [ ] Set up Redis for caching
- [ ] Optimize database queries
- [ ] Configure database connection pooling
- [ ] Enable API response caching

### Monitoring
- [ ] Set up Sentry for error tracking
- [ ] Configure application logging
- [ ] Set up uptime monitoring
- [ ] Configure alerts for errors
- [ ] Set up performance monitoring
- [ ] Configure database monitoring

### Database
- [ ] Run migrations
- [ ] Set up automated backups
- [ ] Configure backup retention
- [ ] Test restore process
- [ ] Set up read replicas (if needed)

### Testing
- [ ] Run all backend tests
- [ ] Run all frontend tests
- [ ] Perform load testing
- [ ] Test authentication flow
- [ ] Test file upload/export
- [ ] Verify email notifications

---

## DNS Configuration

### Point domain to services
```
# A Records
api.resumax.app     → Backend IP/CNAME
resumax.app         → Frontend IP/CNAME
www.resumax.app     → Frontend IP/CNAME

# CNAME Records (if using CDN)
resumax.app         → <cloudfront-domain>.cloudfront.net
api.resumax.app     → <backend-url>.run.app
```

---

## CI/CD Pipeline

### GitHub Actions Example
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy resumax-backend \
            --source ./backend \
            --region us-central1

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and deploy
        run: |
          cd frontend
          npm ci
          npm run build
          firebase deploy --only hosting
```

---

## Rollback Procedure

### Cloud Run
```bash
# List revisions
gcloud run revisions list --service resumax-backend

# Rollback to previous
gcloud run services update-traffic resumax-backend \
  --to-revisions=<previous-revision>=100
```

### Vercel
```bash
# List deployments
vercel list

# Promote deployment
vercel promote <deployment-url>
```

---

## Cost Estimates

### Small Scale (< 1000 users)
- **GCP**: ~$50-100/month
  - Cloud Run: ~$15
  - Cloud SQL: ~$25
  - Firebase Hosting: ~$10
  
- **AWS**: ~$60-120/month
  - Elastic Beanstalk: ~$25
  - RDS: ~$30
  - S3 + CloudFront: ~$10

- **Vercel + Railway**: ~$45/month
  - Vercel Pro: $20
  - Railway: $25

---

## Support & Monitoring

### Recommended Tools
- **Error Tracking**: Sentry
- **Uptime**: UptimeRobot, Pingdom
- **Logs**: Datadog, Logtail
- **Analytics**: Google Analytics, Mixpanel
- **Performance**: New Relic, Datadog APM

---

**Next Steps**: Choose deployment option and follow the corresponding guide above.
