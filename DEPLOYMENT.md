# PlanGram Deployment Guide

**Version**: 1.0.0  
**Last Updated**: August 20, 2026

---

## Table of Contents

1. [Quick Start (Docker)](#quick-start-docker)
2. [Manual Installation](#manual-installation)
3. [Production Deployment](#production-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Security Checklist](#security-checklist)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start (Docker)

### Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

### 5-Minute Setup

```bash
# 1. Clone repository
git clone https://github.com/yourusername/plangram.git
cd plangram

# 2. Configure environment
cp .env.example .env
nano .env  # Edit with your settings

# 3. Start services
docker-compose up -d

# 4. Check status
docker-compose ps

# 5. Open application
open http://localhost
```

**That's it!** PlanGram is now running at:
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

---

## Manual Installation

### Prerequisites

**Backend**:
- Python 3.10+
- GDAL 3.0+
- PostgreSQL 13+ with PostGIS (optional)

**Frontend**:
- Node.js 18+
- npm 9+

### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y gdal-bin libgdal-dev python3-gdal libspatialindex-dev

# 4. Install Python packages
pip install -r requirements.txt

# 5. Configure environment
cp ../.env.example ../.env
nano ../.env

# 6. Run backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Configure environment
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env.local

# 4. Run development server
npm run dev

# Or build for production
npm run build
npm run preview
```

---

## Production Deployment

### Option 1: Docker (Recommended)

**Advantages**:
- Consistent environment
- Easy scaling
- Simple updates
- Includes health checks

**Steps**:

```bash
# 1. Clone on production server
git clone https://github.com/yourusername/plangram.git
cd plangram

# 2. Configure production environment
cp .env.example .env
nano .env
# Set:
# - AI_PROVIDER=gemini (if using AI)
# - GEMINI_API_KEY=your_actual_key
# - BACKEND_RELOAD=false
# - DEBUG=false
# - LOG_LEVEL=WARNING

# 3. Build and start
docker-compose up -d --build

# 4. Verify
curl http://localhost:8000/api/health
curl http://localhost/health
```

### Option 2: Cloud Platforms

#### AWS Deployment

**Services**:
- **Backend**: AWS ECS or EC2
- **Frontend**: S3 + CloudFront
- **Database**: RDS PostgreSQL with PostGIS (optional)

**Steps**:
1. Create ECR repositories for backend/frontend
2. Push Docker images to ECR
3. Create ECS task definitions
4. Deploy to ECS cluster
5. Configure ALB for load balancing
6. Setup CloudFront for frontend

#### Google Cloud Platform

**Services**:
- **Backend**: Cloud Run
- **Frontend**: Firebase Hosting or Cloud Storage
- **Database**: Cloud SQL PostgreSQL (optional)

**Steps**:
1. Build Docker images
2. Push to Google Container Registry
3. Deploy backend to Cloud Run
4. Deploy frontend to Firebase Hosting
5. Configure Cloud Load Balancer

#### Azure Deployment

**Services**:
- **Backend**: Azure Container Instances or App Service
- **Frontend**: Azure Static Web Apps
- **Database**: Azure Database for PostgreSQL (optional)

**Steps**:
1. Create Azure Container Registry
2. Push Docker images
3. Deploy to Container Instances
4. Deploy frontend to Static Web Apps
5. Configure Azure Front Door

### Option 3: Traditional Server

**Requirements**:
- Ubuntu 20.04+ or similar Linux
- Nginx for reverse proxy
- Systemd for process management

**Backend Setup**:

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3.10 python3-pip python3-venv nginx

# Setup application
cd /opt
sudo git clone https://github.com/yourusername/plangram.git
cd plangram/backend
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/plangram-backend.service
```

**Service file** (`/etc/systemd/system/plangram-backend.service`):
```ini
[Unit]
Description=PlanGram Backend API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/plangram/backend
Environment="PATH=/opt/plangram/backend/venv/bin"
ExecStart=/opt/plangram/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start**:
```bash
sudo systemctl enable plangram-backend
sudo systemctl start plangram-backend
sudo systemctl status plangram-backend
```

**Frontend Setup**:

```bash
# Build frontend
cd /opt/plangram/frontend
npm install
npm run build

# Copy to nginx
sudo cp -r dist/* /var/www/plangram/
```

**Nginx Configuration** (`/etc/nginx/sites-available/plangram`):
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Frontend
    location / {
        root /var/www/plangram;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**Enable site**:
```bash
sudo ln -s /etc/nginx/sites-available/plangram /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Environment Configuration

### Required Variables

```env
# AI Configuration (Optional but recommended)
AI_PROVIDER=gemini              # Options: gemini, openai, none
GEMINI_API_KEY=your_key_here    # Get from https://makersuite.google.com/app/apikey

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_RELOAD=false            # Set to false in production
DEBUG=false                      # Set to false in production

# Frontend Configuration
VITE_API_BASE_URL=http://your-domain.com/api

# Data Configuration
DATA_MODE=prototype              # Options: prototype, uploaded, official

# CORS (adjust for your domain)
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com

# GIS Settings
DISTANCE_THRESHOLD_METERS=500
INTERNAL_CRS=EPSG:4326

# Optimization
OPTIMIZATION_TIMEOUT_SECONDS=60

# Logging
LOG_LEVEL=INFO                   # Options: DEBUG, INFO, WARNING, ERROR
```

### Optional Variables

```env
# AI Settings (if using AI)
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2048

# Upload Settings (for future data manager)
MAX_UPLOAD_SIZE_MB=100
UPLOAD_DIR=uploads

# Database (optional, for future use)
DATABASE_URL=postgresql://user:password@localhost:5432/plangram
```

### Getting API Keys

**Gemini API Key** (Free tier available):
1. Visit https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy key to `.env` file

**OpenAI API Key** (Paid):
1. Visit https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy key to `.env` file

---

## Security Checklist

### Before Production Deployment

- [ ] Change all default passwords
- [ ] Set `DEBUG=false`
- [ ] Set `BACKEND_RELOAD=false`
- [ ] Configure proper `CORS_ORIGINS` (not `*`)
- [ ] Use HTTPS (SSL/TLS certificates)
- [ ] Set up firewall (allow only 80, 443)
- [ ] Enable rate limiting
- [ ] Configure proper logging
- [ ] Set up monitoring and alerts
- [ ] Regular backups of data directory
- [ ] Keep dependencies updated
- [ ] Use environment variables for secrets (never commit)
- [ ] Implement authentication (if multi-user)
- [ ] Configure CSP headers
- [ ] Enable HSTS headers

### SSL/TLS Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal (automatic with Let's Encrypt)
sudo certbot renew --dry-run
```

### Firewall Configuration (UFW)

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

---

## Monitoring & Maintenance

### Health Checks

**Backend Health**:
```bash
curl http://localhost:8000/api/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "data_mode": "prototype",
  "ai_provider": "gemini",
  "version": "1.0.0"
}
```

**Frontend Health**:
```bash
curl http://localhost/health
```

### Logging

**Docker Logs**:
```bash
# View logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f backend
```

**Systemd Logs**:
```bash
# Backend logs
sudo journalctl -u plangram-backend -f

# Last 100 lines
sudo journalctl -u plangram-backend -n 100
```

### Monitoring Tools

**Recommended**:
- **Uptime**: UptimeRobot or Pingdom
- **Performance**: New Relic or Datadog
- **Errors**: Sentry
- **Logs**: ELK Stack or Papertrail

### Backup Strategy

**What to backup**:
- `data/` directory (village data, scenarios)
- `.env` file (configuration)
- Database (if using PostgreSQL)

**Backup script**:
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/plangram"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup data directory
tar -czf $BACKUP_DIR/data_$DATE.tar.gz data/

# Backup environment
cp .env $BACKUP_DIR/env_$DATE.txt

# Keep only last 7 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

**Schedule with cron**:
```bash
# Run daily at 2 AM
0 2 * * * /opt/plangram/backup.sh
```

### Updates

**Docker Deployment**:
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Verify
docker-compose ps
curl http://localhost:8000/api/health
```

**Manual Deployment**:
```bash
# Pull latest code
cd /opt/plangram
sudo git pull

# Update backend
cd backend
sudo venv/bin/pip install -r requirements.txt
sudo systemctl restart plangram-backend

# Update frontend
cd ../frontend
npm install
npm run build
sudo cp -r dist/* /var/www/plangram/

# Reload nginx
sudo systemctl reload nginx
```

---

## Troubleshooting

### Common Issues

#### 1. Backend Won't Start

**Symptoms**: `docker-compose up` fails or systemd service fails to start

**Solutions**:
```bash
# Check logs
docker-compose logs backend
# or
sudo journalctl -u plangram-backend -n 50

# Common causes:
# - Port 8000 already in use
#   Solution: Stop other service or change port
# - Missing dependencies
#   Solution: Rebuild Docker image or reinstall packages
# - Invalid .env file
#   Solution: Check syntax, verify all required variables
```

#### 2. GDAL Import Error

**Symptoms**: `ImportError: No module named 'osgeo'`

**Solutions**:
```bash
# Install GDAL system packages
sudo apt-get install gdal-bin libgdal-dev python3-gdal

# Reinstall Python GDAL
pip install GDAL==$(gdal-config --version)
```

#### 3. Frontend Can't Connect to Backend

**Symptoms**: API calls fail with CORS errors

**Solutions**:
1. Check `VITE_API_BASE_URL` in frontend `.env`
2. Verify `CORS_ORIGINS` in backend `.env` includes frontend URL
3. Ensure backend is running: `curl http://localhost:8000/api/health`
4. Check browser console for specific error

#### 4. Docker Container Keeps Restarting

**Symptoms**: Container starts then immediately stops

**Solutions**:
```bash
# Check exit code and logs
docker ps -a
docker logs <container_id>

# Common causes:
# - Application crash on startup
# - Port already in use
# - Missing environment variable
# - Invalid configuration
```

### Getting Help

**Logs to collect**:
- Application logs
- System logs
- Error messages
- Configuration files (redact secrets!)

**Information to provide**:
- Operating system and version
- Docker version (if applicable)
- Python version
- Node.js version
- Steps to reproduce issue

---

## Performance Tuning

### Backend Optimization

**Gunicorn with multiple workers** (replace uvicorn):
```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

**Environment variables**:
```env
# More aggressive timeouts for production
OPTIMIZATION_TIMEOUT_SECONDS=30
```

### Frontend Optimization

**Nginx caching**:
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

**Compression**:
```nginx
gzip on;
gzip_types text/plain text/css text/xml text/javascript application/json;
gzip_min_length 1000;
```

### Database Optimization (if using PostgreSQL)

```sql
-- Create indexes
CREATE INDEX idx_buildings_geom ON buildings USING GIST (geometry);
CREATE INDEX idx_facilities_type ON facilities (facility_type);

-- Analyze tables
ANALYZE buildings;
ANALYZE facilities;
```

---

## Scaling

### Horizontal Scaling

**Load Balancer + Multiple Backends**:
```yaml
# docker-compose-scale.yml
services:
  backend:
    ...
    deploy:
      replicas: 3
  
  nginx:
    ...
    depends_on:
      - backend
```

### Vertical Scaling

**Increase resources**:
```yaml
services:
  backend:
    ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
```

---

## Next Steps

After deployment:

1. ✅ Verify all features work
2. ✅ Test with real user workflows
3. ✅ Monitor performance for 1 week
4. ✅ Set up alerts for downtime/errors
5. ✅ Train users with documentation
6. ✅ Collect feedback for improvements

**For operational questions, see**: `USER_GUIDE.md`  
**For development, see**: `ARCHITECTURE.md` and `README.md`

