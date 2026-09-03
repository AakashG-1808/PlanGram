# PlanGram Architecture

## Overview

PlanGram follows a modular, data-driven architecture designed to support multiple villages and data sources without code changes.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       DATA SOURCES                          │
│  • Built-in representative data                            │
│  • User-uploaded GIS files                                 │
│  • Open/public datasets                                    │
│  • Future official SVAMITVA datasets                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              DATA INGESTION / DATA MANAGER                  │
│  • File validation & CRS handling                          │
│  • Layer mapping & schema transformation                   │
│  • Metadata tracking                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│            COMMON SPATIAL DATA MODEL                        │
│  • Villages, Buildings, Parcels, Roads                     │
│  • Water Bodies, Facilities, Households                    │
│  • Standardized CRS & geometry                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│           SPATIAL ANALYSIS ENGINE                           │
│  • Coverage calculation                                    │
│  • Distance analysis (network & Euclidean)                 │
│  • Accessibility metrics                                   │
│  • Constraint validation                                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              SCENARIO ENGINE                                │
│  • Proposal management                                     │
│  • Before/after simulation                                 │
│  • Scenario comparison                                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│           OPTIMIZATION ENGINE                               │
│  • Candidate location generation                           │
│  • Budget-constrained optimization                         │
│  • Multi-objective scoring                                 │
│  • Google OR-Tools integration                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│               AI PROVIDER LAYER                             │
│  • Provider abstraction (Gemini, Mock)                     │
│  • Intent parsing                                          │
│  • Insight generation                                      │
│  • Recommendation explanation                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│            PLANGRAM WEB UI                                  │
│  • MapLibre GL JS interactive map                          │
│  • Village selector & planning dashboard                   │
│  • Scenario builder & comparison                           │
│  • Data manager interface                                  │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **Mapping**: MapLibre GL JS
- **State Management**: React Context / Zustand (TBD)
- **HTTP Client**: Axios / Fetch API
- **Build Tool**: Vite

### Backend
- **Framework**: FastAPI (Python)
- **Validation**: Pydantic
- **GIS Processing**: GeoPandas, Shapely, GDAL, Rasterio
- **Optimization**: Google OR-Tools
- **AI**: Google Gemini (via abstraction layer)
- **Database**: PostgreSQL + PostGIS
- **ORM**: SQLAlchemy (with GeoAlchemy2)

### Data Storage
- **Spatial Database**: PostgreSQL + PostGIS
- **File Storage**: Local filesystem (uploads/)
- **Configuration**: JSON files (data/)

## Directory Structure

```
plangram/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── pages/          # Full page components
│   │   │   ├── features/       # Feature-specific components
│   │   │   ├── map/            # Map-related components
│   │   │   ├── villages/       # Village selector, info
│   │   │   ├── scenarios/      # Scenario builder, comparison
│   │   │   ├── insights/       # Insights, metrics display
│   │   │   ├── optimization/   # Optimization UI
│   │   │   ├── data-manager/   # Data upload, management
│   │   │   └── ai/             # AI interaction components
│   │   ├── services/           # API client services
│   │   ├── types/              # TypeScript type definitions
│   │   ├── hooks/              # Custom React hooks
│   │   ├── utils/              # Utility functions
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│   ├── app/
│   │   ├── api/                # API route handlers
│   │   │   ├── villages.py
│   │   │   ├── scenarios.py
│   │   │   ├── optimization.py
│   │   │   ├── data_ingestion.py
│   │   │   └── ai.py
│   │   ├── core/               # Core configuration
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/             # Database models
│   │   │   ├── village.py
│   │   │   ├── building.py
│   │   │   ├── scenario.py
│   │   │   └── dataset.py
│   │   ├── schemas/            # Pydantic schemas
│   │   │   ├── village.py
│   │   │   ├── scenario.py
│   │   │   └── data_source.py
│   │   ├── services/           # Business logic services
│   │   │   ├── gis/            # Spatial analysis services
│   │   │   │   ├── coverage.py
│   │   │   │   ├── distance.py
│   │   │   │   ├── constraints.py
│   │   │   │   └── candidates.py
│   │   │   ├── optimization/   # Optimization services
│   │   │   │   └── budget_optimizer.py
│   │   │   ├── scenarios/      # Scenario management
│   │   │   │   └── scenario_service.py
│   │   │   ├── data_ingestion/ # Data upload/import
│   │   │   │   ├── validator.py
│   │   │   │   ├── transformer.py
│   │   │   │   └── importer.py
│   │   │   └── ai/             # AI provider services
│   │   │       ├── provider.py
│   │   │       ├── gemini_provider.py
│   │   │       └── mock_provider.py
│   │   ├── repositories/       # Data access layer
│   │   │   └── village_repository.py
│   │   ├── utils/              # Utility functions
│   │   │   ├── geometry.py
│   │   │   └── data_loader.py
│   │   └── main.py             # FastAPI application
│   ├── requirements.txt
│   └── pytest.ini
│
├── data/
│   ├── village_registry.json
│   ├── cost_config.json
│   ├── source_metadata.json
│   ├── villages/
│   │   ├── village_01/
│   │   │   ├── boundary.geojson
│   │   │   ├── buildings.geojson
│   │   │   ├── parcels.geojson
│   │   │   ├── roads.geojson
│   │   │   ├── water_bodies.geojson
│   │   │   ├── facilities.geojson
│   │   │   └── households.csv
│   │   └── village_02/
│   │       └── (same structure)
│   └── reference/
│       └── source_notes.json
│
├── docs/
│   ├── ARCHITECTURE.md         # This file
│   ├── DATA_SCHEMA.md
│   ├── DATA_SOURCES.md
│   ├── DATA_INGESTION.md
│   ├── AI_METHODOLOGY.md
│   ├── OPTIMIZATION.md
│   ├── DEMO_GUIDE.md
│   └── ASSUMPTIONS.md
│
├── uploads/                     # User-uploaded files
├── .env.example
├── .gitignore
└── README.md
```

## Core Principles

### 1. Data-Driven Configuration
- Village-specific behavior comes from data, not code
- Infrastructure types are configurable
- Cost models are external configuration
- Constraints are data-driven

### 2. Modular Design
- Clear separation of concerns
- Each engine (spatial, scenario, optimization) is independent
- Pluggable AI providers
- Testable components

### 3. Transparency
- All data sources are clearly labeled
- Calculations are deterministic and explainable
- Cost assumptions are documented
- AI recommendations are grounded in calculated metrics

### 4. Extensibility
- New villages can be added without code changes
- New infrastructure types via configuration
- New data sources through data manager
- Additional AI providers through abstraction

## Data Flow Examples

### Example 1: View Village
```
User selects village
    ↓
GET /api/villages/{id}
    ↓
Village Repository loads from DB/filesystem
    ↓
Spatial Analysis Engine calculates current metrics
    ↓
AI Provider generates insights (optional)
    ↓
JSON response with village data + metrics
    ↓
Frontend renders map + insights
```

### Example 2: Propose Facility
```
User places water facility on map
    ↓
POST /api/villages/{id}/simulate
    ↓
Constraint Engine validates location
    ↓
Spatial Analysis Engine calculates coverage
    ↓
Before/after comparison
    ↓
JSON response with simulation results
    ↓
Frontend updates map + metrics in real-time
```

### Example 3: Optimize Budget
```
User enters budget ₹10,00,000
    ↓
POST /api/villages/{id}/optimize
    ↓
Candidate Engine generates feasible locations
    ↓
Optimization Engine (OR-Tools) generates plans
    ↓
Scoring & ranking
    ↓
AI Provider explains recommendation
    ↓
JSON response with multiple plans + explanation
    ↓
Frontend displays scenario comparison
```

## API Design Principles

- RESTful endpoints
- JSON request/response
- Consistent error handling
- Pagination for large datasets
- GeoJSON for spatial data
- Clear HTTP status codes

## Security Considerations

- Environment variables for secrets
- Input validation (file types, sizes, CRS)
- SQL injection prevention (ORM)
- File upload restrictions
- CORS configuration
- Rate limiting (future)

## Performance Considerations

- Lazy-load map layers
- Simplify geometries for frontend display
- Cache repeated calculations
- Spatial indexes on database
- Process large GIS files server-side
- Background jobs for heavy processing (future)

## Scalability Path

Current (Phase 1-12): 2 villages, single server

Future possibilities:
- Multiple Panchayats (10-100 villages)
- Microservices architecture
- Caching layer (Redis)
- Message queue (Celery)
- Cloud deployment (AWS/GCP/Azure)

## Development Workflow

1. Develop features locally
2. Test with synthetic data
3. Validate with sample real data
4. Deploy to staging
5. User testing with planning officials
6. Production deployment with official data

---

**Note**: This architecture prioritizes clarity, modularity, and transparency over premature optimization. Performance enhancements will be added based on actual usage patterns.
