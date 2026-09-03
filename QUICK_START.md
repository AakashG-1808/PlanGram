# PlanGram Quick Start Guide

**Get PlanGram running in 5 minutes!**

---

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- 4GB RAM minimum
- 2GB disk space

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

#### Terminal 1 — Backend:
```bash
cd backend
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows Command Prompt:
# venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

#### Terminal 2 — Frontend:
```bash
cd frontend
npm install
npm run dev
```

### 3. Open Application

Open in your browser:
- **Application**: http://localhost:5173
- **API Docs**: http://localhost:8000/api/docs

**That's it!** PlanGram is now running with demo village data.

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

## Configuration

### Enable AI Features

1. Get Gemini API key: https://makersuite.google.com/app/apikey
2. Edit `.env`:
   ```env
   AI_PROVIDER=gemini
   GEMINI_API_KEY=your_actual_key_here
   ```
3. Restart the backend service.

---

## Troubleshooting

### Port Already in Use

**Error**: `Address already in use` (port 8000 or 5173)

**Solution**:
- If port 8000 is occupied, run backend on an alternate port:
  ```bash
  python -m uvicorn app.main:app --port 8001 --reload
  ```
- Vite will automatically prompt or select port 5174 if port 5173 is in use.

### Backend Not Starting

**Common fixes**:
- Verify Python virtual environment is activated (`(venv)` shown in terminal)
- Run `pip install -r requirements.txt` to ensure all GIS and web dependencies are installed
- Check that `.env` exists in the repository root

### Frontend Can't Connect to Backend

**Solution**:
1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check browser console for errors
3. Ensure backend CORS allows `http://localhost:5173` (configured by default in `.env.example`)

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

---

**PlanGram - Explore. Simulate. Plan.**  
*Infrastructure planning made easy* 🚀
