# PlanGram Documentation

Welcome to the PlanGram documentation. This directory contains comprehensive technical documentation for the system.

## Documentation Index

### Core Documentation

1. **[ARCHITECTURE.md](ARCHITECTURE.md)**
   - System architecture overview
   - Technology stack
   - Directory structure
   - Data flow examples
   - API design principles
   - Security and performance considerations

2. **[DATA_SCHEMA.md](DATA_SCHEMA.md)**
   - Complete data model
   - Entity definitions (Village, Building, Parcel, etc.)
   - Attribute specifications
   - Validation rules
   - Database schema (PostgreSQL + PostGIS)
   - File format standards

3. **[DATA_SOURCES.md](DATA_SOURCES.md)**
   - Data source types (REAL_OFFICIAL, OPEN_PUBLIC, ESTIMATED, SYNTHETIC)
   - Data acquisition guide
   - SVAMITVA data integration
   - OpenStreetMap usage
   - Data validation checklist
   - Attribution requirements

4. **[ASSUMPTIONS.md](ASSUMPTIONS.md)**
   - Data assumptions (population, demographics, spatial)
   - Technical assumptions (GIS, optimization, AI)
   - Prototype synthetic data details
   - System limitations
   - Planning limitations
   - Responsible use guidelines

### Additional Documentation (To Be Created)

5. **DATA_INGESTION.md** (Phase 9)
   - Upload workflow
   - File format support
   - CRS handling
   - Layer mapping
   - Validation process

6. **AI_METHODOLOGY.md** (Phase 10)
   - AI provider architecture
   - Planning copilot usage
   - Insight generation
   - Recommendation explanation
   - Limitations and fallbacks

7. **OPTIMIZATION.md** (Phase 7)
   - Budget optimization algorithms
   - Candidate location generation
   - Impact scoring methodology
   - OR-Tools integration
   - Multi-objective optimization

8. **DEMO_GUIDE.md** (Phase 12)
   - Step-by-step demo walkthrough
   - Hero use case demonstration
   - Expected results
   - Common questions

## Quick Reference

### For Developers
- Start with **ARCHITECTURE.md** for system overview
- Refer to **DATA_SCHEMA.md** for data structures
- Check **ASSUMPTIONS.md** for limitations and caveats

### For Planners/Users
- Read **ASSUMPTIONS.md** first to understand data and limitations
- Review **DATA_SOURCES.md** for data quality understanding
- See **DEMO_GUIDE.md** (Phase 12) for usage instructions

### For Data Managers
- **DATA_SOURCES.md** for acquisition guidance
- **DATA_SCHEMA.md** for required structure
- **DATA_INGESTION.md** (Phase 9) for upload process

## Documentation Standards

### Metadata
Each document includes:
- Version number
- Last updated date
- Change history (future)

### Structure
- Clear table of contents
- Code examples where appropriate
- Visual diagrams when helpful
- Real-world examples

### Maintenance
- Documents updated with each phase
- Breaking changes clearly marked
- Deprecation notices included

## External Resources

### Technology Documentation
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [MapLibre GL JS](https://maplibre.org/)
- [GeoPandas](https://geopandas.org/)
- [Google OR-Tools](https://developers.google.com/optimization)

### GIS Resources
- [EPSG:4326 Reference](https://epsg.io/4326)
- [GeoJSON Specification](https://geojson.org/)
- [PostGIS Documentation](https://postgis.net/documentation/)

### Government Resources
- SVAMITVA Portal (requires authorization)
- [Bhuvan (ISRO)](https://bhuvan.nrsc.gov.in/)
- [OpenStreetMap India](https://openstreetmap.in/)

## Contributing to Documentation

### Style Guide
- Use clear, concise language
- Include practical examples
- Explain "why" not just "what"
- Keep technical jargon minimal
- Use bullet points and tables liberally

### Updating Documentation
1. Make changes in appropriate .md file
2. Update version/date at bottom
3. Update this README if new docs added
4. Test all code examples
5. Review for clarity

## Documentation Roadmap

| Document | Phase | Status |
|----------|-------|--------|
| ARCHITECTURE.md | 1 | ✅ Complete |
| DATA_SCHEMA.md | 1 | ✅ Complete |
| DATA_SOURCES.md | 1 | ✅ Complete |
| ASSUMPTIONS.md | 1 | ✅ Complete |
| DATA_INGESTION.md | 9 | 📋 Planned |
| AI_METHODOLOGY.md | 10 | 📋 Planned |
| OPTIMIZATION.md | 7 | 📋 Planned |
| DEMO_GUIDE.md | 12 | 📋 Planned |

## Questions?

If documentation is unclear or incomplete:
1. Check if it's a future phase (see roadmap above)
2. Review related documentation
3. Check code comments for implementation details
4. Refer to master prompt for original specifications

---

**Documentation Version**: 1.0.0  
**Last Updated**: 2026-08-20  
**Phase**: 1 - Foundation
