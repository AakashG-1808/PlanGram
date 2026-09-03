# PlanGram Deployment Guide

**Version**: 1.0.0  
**Last Updated**: August 20, 2026

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local & Development Setup](#local--development-setup)
3. [Production Deployment](#production-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Security Checklist](#security-checklist)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Backend Requirements:
- Python 3.10+
- GDAL 3.0+ (for GIS data handling)
- libspatialindex-dev (for R-tree indexing)
- PostgreSQL 13+ with PostGIS (optional; in-memory GeoPandas mode supported)

### Frontend Requirements:
- Node.js 18+
- npm 9+

---

## Local & Development Setup

### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows Command Prompt:
# venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

# 3. Install system dependencies (Ubuntu/Debian if applicable)
sudo apt-get update
sudo apt-get install -y gdal-bin libgdal-dev python3-gdal libspatialindex-dev

# 4. Install Python packages
pip install --upgrade pip
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

### Production Server (Ubuntu / Linux)

**Components**:
- **Reverse Proxy**: Nginx (serves built frontend and proxies `/api` to FastAPI)
- **Process Manager**: Systemd or PM2 (keeps FastAPI uvicorn/gunicorn running)

#### 1. Setup Application Files

```bash
sudo apt-get update
sudo apt-get install -y python3.10 python3-pip python3-venv nginx

# Clone repository to deployment folder
cd /opt
sudo git clone https://github.com/yourusername/plangram.git
cd plangram

# Setup backend
cd backend
sudo python3 -m venv venv
sudo venv/bin/pip install --upgrade pip
sudo venv/bin/pip install -r requirements.txt

# Setup production environment config
sudo cp ../.env.example ../.env
# Configure production variables (AI keys, DEBUG=false, etc.)
```

#### 2. Create Systemd Service for Backend

Create `/etc/systemd/system/plangram-backend.service`:

```ini
[Unit]
Description=PlanGram Backend API Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/plangram/backend
ExecStart=/opt/plangram/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5
EnvironmentFile=/opt/plangram/.env

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable plangram-backend
sudo systemctl start plangram-backend
```

#### 3. Build Frontend & Configure Nginx

```bash
cd /opt/plangram/frontend
npm install
npm run build

# Deploy build to web root
sudo mkdir -p /var/www/plangram
sudo cp -r dist/* /var/www/plangram/
```

Configure Nginx `/etc/nginx/sites-available/plangram`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/plangram;
    index index.html;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Static asset caching
    location ~* \.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip
    gzip on;
    gzip_types text/plain text/css text/xml text/javascript application/json;
}
```

Enable Nginx site:
```bash
sudo ln -s /etc/nginx/sites-available/plangram /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Environment Configuration

### Required Variables (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_MODE` | `prototype` | `prototype` (GeoJSON/Shapefile) or `production` (PostGIS) |
| `BACKEND_HOST` | `0.0.0.0` | Bind host address |
| `BACKEND_PORT` | `8000` | Bind port number |
| `DEBUG` | `false` | Enable debug mode (set to `false` in production) |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed origins separated by commas |

### Optional AI Configuration

| Variable | Description |
|----------|-------------|
| `AI_PROVIDER` | `none` or `gemini` |
| `GEMINI_API_KEY` | Google Gemini API key |

---

## Security Checklist

- [ ] `DEBUG=false` in production `.env`
- [ ] Restrict `CORS_ORIGINS` to trusted domains
- [ ] Serve application over HTTPS with SSL certificates (e.g., Certbot / Let's Encrypt)
- [ ] Keep API keys protected with appropriate file permissions (`chmod 600 .env`)
- [ ] Set up firewall rules (allow 80, 443, restrict 8000 to internal proxy)

---

## Monitoring & Maintenance

### Service Health Checks

```bash
curl http://127.0.0.1:8000/api/health
```

### Viewing Logs

```bash
# Backend systemd logs
sudo journalctl -u plangram-backend -f

# Nginx access & error logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Updating Application

```bash
cd /opt/plangram
sudo git pull

# Backend update
cd backend
sudo venv/bin/pip install -r requirements.txt
sudo systemctl restart plangram-backend

# Frontend update
cd ../frontend
npm install
npm run build
sudo cp -r dist/* /var/www/plangram/
sudo systemctl reload nginx
```

---

## Troubleshooting

### Backend Service Fails to Start

```bash
sudo journalctl -u plangram-backend -n 50 --no-pager
```

**Common Causes**:
- Port conflict: Check `sudo lsof -i :8000`
- Missing GDAL dependencies: Verify `python -c "import shapely; import geopandas"`
- Virtual environment issues: Reinstall requirements in `venv`

### Frontend API Connection Errors

- Ensure `VITE_API_BASE_URL` points to the correct backend host/path.
- Verify `CORS_ORIGINS` in `.env` includes the frontend origin.
