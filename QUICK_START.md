# PlanGram Quick Start Guide

**Get PlanGram running in 5 minutes!**

---

## Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

**Don't have Docker?** [Install Docker](https://docs.docker.com/get-docker/)

---

## Quick Start (3 Steps)

### 1. Clone and Configure

```bash
# Clone repository
git clone https://github.com/yourusername/plangram.git
cd plangram

# Copy environment template
cp .env.example .env

# (Optional) Edit .env to add Gemini API key for AI features
nano .env
```

### 2. Start Services

```bash
docker-compose up -d
```

Wait 30-60 seconds for services to start.

### 3. Open Application

Open in your browser:
- **Application**: http://localhost
- **API Docs**: http://localhost:8000/api/docs

**That's it!** PlanGram is now running with 2 demo villages.

---

## What's Included

✅ **Backend API**: Full optimization engine (35 endpoints)  
✅ **Frontend**: Interactive map interface  
✅ **2 Demo Villages**: Chikkahullur and Bandapalya  
✅ **Complete GIS Data**: Buildings, roads, facilities, parcels  
✅ **AI Features**: Natural language queries (optional)

---

## First Steps

### 1. Explore the Map

1. Select "Chikkahullur" from village dropdown
2. Toggle map layers to see buildings, roads, facilities
3. Zoom and pan to explore the village

### 2. Run Coverage Analysis

1. Note current coverage % in metrics panel
2. Adjust distance threshold slider (default: 500m)
3. See which areas are underserved (red/yellow)

### 3. Optimize Placement

1. Set budget (e.g., ₹300,000)
2. Click "Optimize"
3. See recommended facility locations
4. Review coverage improvement and cost efficiency

### 4. Try AI Features (if configured)

1. Type: "Find best water facility location in village_01 with budget 200000"
2. Click "Explain" on any recommended location
3. Generate insights from analysis

---

## Manual Setup (Without Docker)

### Backend

```bash
cd backend
python -m venv venv

# Activate virtual environment:
# Windows PowerShell: .\venv\Scripts\Activate.ps1
# Windows CMD: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

.\venv\Scripts\Activate.ps1  # For Windows PowerShell

# Install dependencies (skip database packages if needed)
pip install --upgrade pip setuptools wheel
pip install fastapi uvicorn pydantic pydantic-settings python-multipart python-dotenv
pip install numpy pandas shapely geopandas pyproj
pip install google-generativeai pytest pytest-asyncio httpx loguru

# Start server
python -m uvicorn app.main:app --reload
```

**Backend will run on**: http://127.0.0.1:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

**Frontend will run on**: http://localhost:5173

---

## Useful Commands

### Check Status

```bash
docker-compose ps
```

### View Logs

```bash
docker-compose logs -f
```

### Stop Services

```bash
docker-compose down
```

### Restart Services

```bash
docker-compose restart
```

### Update to Latest Version

```bash
git pull
docker-compose down
docker-compose up -d --build
```

---

## Configuration

### Enable AI Features

1. Get Gemini API key: https://makersuite.google.com/app/apikey
2. Edit `.env`:
   ```env
   AI_PROVIDER=gemini
   GEMINI_API_KEY=your_actual_key_here
   ```
3. Restart: `docker-compose restart`

### Change Ports

Edit `docker-compose.yml`:
```yaml
frontend:
  ports:
    - "8080:80"  # Change 8080 to your preferred port

backend:
  ports:
    - "9000:8000"  # Change 9000 to your preferred port
```

---

## Troubleshooting

### Port Already in Use

**Error**: `port is already allocated`

**Solution**:
```bash
# Stop conflicting service or change port in docker-compose.yml
docker-compose down
# Edit docker-compose.yml to use different port
docker-compose up -d
```

### Backend Not Starting

**Check logs**:
```bash
docker-compose logs backend
```

**Common fixes**:
- Verify `.env` file exists
- Check Python syntax in error message
- Restart: `docker-compose restart backend`

### Frontend Can't Connect to Backend

**Solution**:
1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check browser console for errors
3. Verify `VITE_API_BASE_URL` in frontend `.env.local`

---

## Next Steps

📖 **Read the User Guide**: `docs/USER_GUIDE.md`  
🚀 **Deploy to Production**: `DEPLOYMENT.md`  
🏗️ **Learn the Architecture**: `docs/ARCHITECTURE.md`  
📊 **API Reference**: http://localhost:8000/api/docs

---

## Getting Help

- **Documentation**: Check `/docs` folder
- **API Docs**: http://localhost:8000/api/docs
- **Issues**: GitHub Issues (if applicable)
- **Support**: Contact your administrator

---

**PlanGram - Explore. Simulate. Plan.**  
*Infrastructure planning made easy* 🚀
