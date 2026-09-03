# PlanGram

PlanGram is a simple planning tool that helps people study village maps and decide where to place infrastructure such as water facilities, community services, or other public assets.

It is built for planning teams, local officials, NGOs, and researchers who want to understand:

- where services are currently weak or missing,
- how many households may benefit,
- which possible locations are best,
- and how different budgets and choices affect the outcome.

---

## What this program does

PlanGram helps turn a map into a planning decision.

Instead of guessing where a facility should go, the system can:

- show a village or area on a map,
- highlight underserved regions,
- suggest possible facility locations,
- estimate costs and coverage,
- compare different scenarios,
- and recommend the best option within a budget.

This makes it easier to plan public infrastructure in a more informed and fair way.

---

## Simple example

Imagine a village where many homes are far from a water access point.

With PlanGram, you can:

1. open the village map,
2. see which households are underserved,
3. choose one or more potential facility locations,
4. set a project budget,
5. generate several possible plans,
6. compare them by coverage, cost, and impact,
7. pick the best option.

---

## Who this is for

This project is meant for people who work on rural planning and local development, including:

- village planners,
- government officials,
- NGOs and field teams,
- local development agencies,
- researchers and students.

It is designed to make planning easier for non-technical users as well.

---

## How it works

PlanGram follows a simple workflow:

1. Select a village or map area
2. Review current access and service gaps
3. Add or adjust facility locations
4. Set a budget and constraints
5. Run planning and optimization logic
6. Compare possible solutions
7. Review the recommendation and decide

The main idea is simple: test ideas before building anything.

---

## What is included in the project

This repository includes:

- a frontend app for the map and dashboard,
- a backend API for analysis and optimization,
- sample village data for demo use,
- GIS and planning logic for coverage analysis,
- optional AI features for explanations and natural language queries.

---

## Quick start

### 1. Clone the project

```bash
git clone https://github.com/yourusername/plangram.git
cd plangram
```

### 2. Set up environment file

```bash
cp .env.example .env
```

If you want AI-based explanations, add your API key in the environment file. If not, the demo version can still run without it.

### 3. Start the services

#### Backend

```bash
cd backend
python -m venv venv

# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Or Windows Command Prompt
# venv\Scripts\activate

# Or macOS/Linux
# source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The backend will run at:

- http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/api/docs

#### Frontend

Open a second terminal and run:

```bash
cd frontend
npm install
npm run dev
```

The frontend will run at:

- http://localhost:5173

### 4. Open the app

Once both are running, open the frontend in your browser:

- http://localhost:5173

You should now see the project running with demo village data.

---

## Default demo data

The project already includes sample village data so you can explore it immediately without needing external files.

This is useful for:

- learning how the tool works,
- testing scenarios,
- showing results to stakeholders,
- and evaluating the planning flow before using real data.

---

## How to use the app

After opening the app, you can:

1. choose a village,
2. view the map and current coverage,
3. identify underserved areas,
4. adjust planning parameters and budget,
5. run optimization,
6. compare multiple options,
7. review the suggested plan.

This is a decision-support tool, which means it helps you understand trade-offs and makes recommendation easier, but final decisions still belong to planners or officials.

---

## Project structure

A simple overview of the workspace:

- [backend](backend) — API and planning logic
- [frontend](frontend) — web interface
- [data](data) — sample GIS and village data
- [docs](docs) — project documentation
- [scripts](scripts) — helper scripts and tests

---

## Need more details?

For deeper technical details, see:

- [QUICK_START.md](QUICK_START.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md)
- [docs/USER_GUIDE.md](docs/USER_GUIDE.md)

---

## Important note

This project is a planning prototype. It is designed to support decisions, not replace official planning authority. The included demo data is for learning and demonstration purposes.

---

## License

This project is currently provided as a local development project. License details may be added later.
