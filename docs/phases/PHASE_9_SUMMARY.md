# Phase 9 Summary - Data Manager Specification

## Status
**Specification**: ✅ Complete  
**Implementation**: ⏳ Not Started (Design phase only)  
**Priority**: Medium

## Overview
Phase 9 specification defines a complete data management system for uploading, validating, transforming, and registering custom village GIS data. This would enable PlanGram to work with real villages beyond the 2 prototype villages.

## What Was Delivered

### Complete Design Specification
- ✅ System architecture diagram
- ✅ API specification (7 endpoints)
- ✅ Data validation rules
- ✅ Attribute mapping system
- ✅ Frontend UI mockups (4 pages)
- ✅ Implementation plan (12 days estimated)
- ✅ Testing strategy
- ✅ Security considerations

## Key Features (Specified)

### 1. File Upload System
- Support formats: GeoJSON, Shapefile, KML, CSV
- Multi-file upload (drag & drop)
- Size limits: 100MB per file, 500MB total
- Temporary storage with cleanup

### 2. Data Validation
- Format detection and parsing
- CRS auto-detection
- Geometry validation (no self-intersections)
- Schema compliance checking
- Required vs optional layers
- Error reporting with severity levels

### 3. CRS Transformation
- Auto-detect source CRS
- Transform to EPSG:4326 (WGS84)
- Support common CRS:
  - EPSG:4326 (WGS84)
  - EPSG:32643 (UTM 43N - Karnataka)
  - EPSG:32644 (UTM 44N)

### 4. Attribute Mapping
- Auto-detection heuristics
- Manual mapping interface
- Common field patterns:
  - building_id, households, facility_type
  - parcel_type, owner_type, road_type

### 5. Village Registration
- Metadata collection (name, taluk, district, state)
- File organization (data/villages/{id}/)
- Registry update (village_registry.json)
- Data source tracking

## API Endpoints (Designed)

```
POST   /api/data/upload         # Upload files
POST   /api/data/validate       # Validate uploaded data
POST   /api/data/transform      # Transform CRS & map attributes
GET    /api/data/preview        # Preview data on map
POST   /api/data/register       # Register village
GET    /api/data/villages       # List all villages
DELETE /api/data/villages/{id}  # Delete village
```

## Workflow (Specified)

```
1. Upload Files
   ↓
2. Validate Data (format, CRS, geometry, schema)
   ↓
3. Preview & Map Attributes
   ↓
4. Transform (CRS + attribute mapping)
   ↓
5. Register Village
   ↓
6. Village Available for Analysis/Optimization
```

## Required Layers

| Layer | Mandatory | Description |
|-------|-----------|-------------|
| boundary | Yes | Village boundary polygon |
| buildings | Yes | Building polygons/points |
| facilities | Recommended | Infrastructure points |
| parcels | Optional | Land ownership |
| roads | Optional | Road network |
| water_bodies | Optional | Water features |
| households | Optional | Demographics (CSV) |

## Validation Rules

### Boundary Layer
- 1 polygon feature required
- Valid geometry (no self-intersections)
- Area > 0

### Buildings Layer
- ≥1 features required
- All within boundary
- Required fields: building_id, households

### Facilities Layer
- Point features
- Required fields: facility_id, facility_type
- Valid types: water, waste, health, education

## Technology Stack (Proposed)

### Backend
- **FastAPI**: Multipart file upload
- **GeoPandas**: GeoJSON & Shapefile parsing
- **Fiona**: Format conversion
- **Shapely**: Geometry validation
- **PyProj**: CRS transformation

### Frontend
- **react-dropzone**: Drag & drop upload
- **Progress bars**: Upload progress
- **MapLibre GL JS**: Preview map
- **Form components**: Attribute mapping

## Implementation Estimate

| Phase | Days | Description |
|-------|------|-------------|
| 9.1 File Upload | 2 | Multipart upload, storage |
| 9.2 Validation | 3 | Format/CRS/geometry validation |
| 9.3 Transformation | 2 | CRS transform, attribute mapping |
| 9.4 Registration | 2 | Village registration, registry update |
| 9.5 Frontend UI | 3 | 4-step wizard UI |
| **Total** | **12 days** | Complete data manager |

## Security Considerations

1. **File Type Whitelist**: Only .geojson, .shp, .kml, .csv
2. **Size Limits**: 100MB per file, 500MB total
3. **Path Sanitization**: Prevent path traversal attacks
4. **Rate Limiting**: Max 5 uploads per hour
5. **Virus Scanning**: Optional ClamAV integration

## Success Criteria (When Implemented)

1. Upload GeoJSON files successfully
2. Upload Shapefile (with .shx, .dbf, .prj) successfully
3. Auto-detect and transform CRS
4. Validate geometry and attributes
5. Auto-detect attributes with >80% accuracy
6. Register village and enable optimization
7. Complete workflow in < 5 minutes

## Why Specification Only?

**Current State**:
- Backend optimization engine: **100% complete**
- All 7 core phases: **Integrated and tested**
- Data manager: **Not immediately needed** (2 prototype villages sufficient)

**Recommendation**:
- **Phase 10 (AI Integration)** or **Phase 12 (Polish)** are higher priority
- Phase 9 becomes critical when:
  - Real SVAMITVA data becomes available
  - Multiple villages need to be added
  - Production deployment with real users

**This specification provides**:
- Complete roadmap for implementation when needed
- Clear API contracts for frontend development
- Validation rules for data quality
- Security and testing considerations

## Files Created

1. `PHASE_9_SPECIFICATION.md` - Complete design spec (18 pages)
2. `PHASE_9_SUMMARY.md` - This summary

## Next Steps

### Option A: Skip to Phase 10 (AI Integration)
- Natural language queries
- Recommendation explanations
- Intent parsing
- **Higher value for demo/polish**

### Option B: Skip to Phase 12 (Demo + Polish)
- Error handling refinement
- Loading states and UX
- Documentation and guides
- Production deployment prep
- **Faster to production-ready state**

### Option C: Implement Phase 9 (Data Manager)
- Enable custom village uploads
- Real data integration
- Multi-village support
- **Needed for production with real users**

## Recommendation

**Proceed with Phase 10 (AI) or Phase 12 (Polish)** rather than implementing Phase 9 now.

**Rationale**:
1. Backend is 100% functional with 2 villages
2. Data upload is complex (12 days estimated)
3. Not needed for demo or testing current capabilities
4. Can be implemented later when real data is available

**Phase 9 Status**: ✅ **SPECIFICATION COMPLETE**  
Ready for implementation when needed.

---

*PlanGram - Explore. Simulate. Plan.*  
*Phase 9: Fully Specified, Implementation Deferred to Production Phase*
