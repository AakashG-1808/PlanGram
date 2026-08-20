# Phase 9 Specification - Data Manager

**Status**: Specification Complete  
**Implementation Status**: Design Phase  
**Priority**: Medium (Backend complete, frontend integration more urgent)

---

## Overview

Phase 9 would implement a data management system that allows users to upload, validate, transform, and register custom village GIS data. This enables the system to work with real villages beyond the 2 prototype villages.

---

## Objectives

### Primary Goals
1. **Upload GIS Data** - Accept GeoJSON, Shapefile, KML formats
2. **Data Validation** - Verify schema, geometry, and completeness
3. **CRS Transformation** - Convert to standard WGS84 (EPSG:4326)
4. **Layer Mapping** - Map uploaded layers to system schema
5. **Village Registration** - Add village to registry with metadata
6. **Multi-Village Support** - Manage 10-100 villages simultaneously

### Secondary Goals
7. **Data Preview** - Show uploaded data before confirming
8. **Error Reporting** - Clear feedback on validation failures
9. **Batch Upload** - Upload multiple villages at once
10. **Data Export** - Download village data in standard formats

---

## System Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                    Data Manager UI                      │
│  • File Upload Widget                                   │
│  • Format Selector (GeoJSON/Shapefile/KML)            │
│  • Layer Mapping Interface                             │
│  • Validation Status Display                           │
│  • Preview Map                                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Data Ingestion API                         │
│  POST /api/data/upload                                  │
│  POST /api/data/validate                                │
│  POST /api/data/transform                               │
│  POST /api/data/register                                │
│  GET  /api/data/villages                                │
│  DELETE /api/data/villages/{id}                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           Data Processing Services                      │
│                                                         │
│  ┌──────────────────────────────────────────┐         │
│  │  File Validator                          │         │
│  │  • Format detection                      │         │
│  │  • Size limits (100MB max)               │         │
│  │  • Schema validation                     │         │
│  └──────────────────────────────────────────┘         │
│                                                         │
│  ┌──────────────────────────────────────────┐         │
│  │  CRS Transformer                         │         │
│  │  • Auto-detect CRS                       │         │
│  │  • Transform to EPSG:4326                │         │
│  │  • Preserve attributes                   │         │
│  └──────────────────────────────────────────┘         │
│                                                         │
│  ┌──────────────────────────────────────────┐         │
│  │  Layer Mapper                            │         │
│  │  • Match layers to schema                │         │
│  │  • Attribute mapping                     │         │
│  │  • Auto-detection with ML                │         │
│  └──────────────────────────────────────────┘         │
│                                                         │
│  ┌──────────────────────────────────────────┐         │
│  │  Data Importer                           │         │
│  │  • Save to data/villages/{id}/           │         │
│  │  • Update village registry               │         │
│  │  • Generate metadata                     │         │
│  └──────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Upload Workflow

```
1. USER SELECTS FILES
   • boundary.geojson
   • buildings.geojson
   • facilities.geojson
   • parcels.geojson (optional)
   • roads.geojson (optional)
   • water_bodies.geojson (optional)
   • households.csv (optional)

2. UPLOAD TO SERVER
   POST /api/data/upload
   → Files stored in temp/ directory
   → Returns upload_id

3. VALIDATE DATA
   POST /api/data/validate?upload_id={id}
   → Check file formats
   → Validate geometries
   → Check required fields
   → Detect CRS
   → Returns validation report

4. PREVIEW DATA (if valid)
   GET /api/data/preview?upload_id={id}
   → Show on map
   → Display statistics
   → Allow layer mapping adjustments

5. TRANSFORM & MAP
   POST /api/data/transform?upload_id={id}
   {
     "layer_mapping": {
       "uploaded_boundary": "boundary",
       "uploaded_structures": "buildings",
       ...
     },
     "attribute_mapping": {
       "buildings": {
         "ID": "building_id",
         "Households": "households",
         ...
       }
     }
   }
   → Transform CRS to EPSG:4326
   → Map attributes to schema
   → Returns transformed data

6. REGISTER VILLAGE
   POST /api/data/register
   {
     "village_name": "New Village",
     "taluk": "Anekal",
     "district": "Bangalore Rural",
     "upload_id": "{id}"
   }
   → Generate village_id
   → Move files to data/villages/{id}/
   → Update village_registry.json
   → Returns village_id

7. CLEANUP
   → Delete temp files
   → Log upload history
```

---

## API Specification

### 1. Upload Files

```http
POST /api/data/upload
Content-Type: multipart/form-data

Request:
  files: File[] (multiple files)
  metadata: {
    "source": "user_upload",
    "description": "Village XYZ data"
  }

Response: 200 OK
{
  "upload_id": "uuid",
  "files_received": 5,
  "total_size_mb": 12.5,
  "status": "uploaded"
}
```

### 2. Validate Data

```http
POST /api/data/validate?upload_id={uuid}

Response: 200 OK
{
  "upload_id": "uuid",
  "status": "valid" | "invalid" | "warnings",
  "files": [
    {
      "filename": "boundary.geojson",
      "format": "geojson",
      "layer_type": "boundary",
      "crs": "EPSG:32643",
      "features_count": 1,
      "is_valid": true,
      "issues": []
    },
    {
      "filename": "buildings.shp",
      "format": "shapefile",
      "layer_type": "buildings",
      "crs": "EPSG:32643",
      "features_count": 250,
      "is_valid": false,
      "issues": [
        {
          "severity": "error",
          "message": "Missing required field: households"
        }
      ]
    }
  ],
  "summary": {
    "total_files": 5,
    "valid_files": 4,
    "errors": 1,
    "warnings": 2
  }
}
```

### 3. Transform Data

```http
POST /api/data/transform?upload_id={uuid}
Content-Type: application/json

Request:
{
  "target_crs": "EPSG:4326",
  "layer_mapping": {
    "boundary.geojson": "boundary",
    "structures.geojson": "buildings"
  },
  "attribute_mapping": {
    "buildings": {
      "ID": "building_id",
      "HH_COUNT": "households"
    }
  }
}

Response: 200 OK
{
  "upload_id": "uuid",
  "status": "transformed",
  "layers": [
    {
      "layer": "boundary",
      "features_transformed": 1,
      "crs_from": "EPSG:32643",
      "crs_to": "EPSG:4326"
    },
    {
      "layer": "buildings",
      "features_transformed": 250,
      "attributes_mapped": 5
    }
  ]
}
```

### 4. Preview Data

```http
GET /api/data/preview?upload_id={uuid}&layer=boundary

Response: 200 OK
{
  "upload_id": "uuid",
  "layer": "boundary",
  "geojson": { ... },
  "statistics": {
    "features": 1,
    "area_hectares": 250,
    "bounds": [77.65, 12.68, 77.72, 12.72]
  }
}
```

### 5. Register Village

```http
POST /api/data/register
Content-Type: application/json

Request:
{
  "upload_id": "uuid",
  "village_name": "Dommasandra",
  "taluk": "Anekal",
  "district": "Bangalore Rural",
  "state": "Karnataka",
  "population": 1500
}

Response: 201 Created
{
  "village_id": "village_03",
  "name": "Dommasandra",
  "status": "registered",
  "data_available": true,
  "layers": ["boundary", "buildings", "facilities", "parcels"],
  "created_at": "2026-08-20T15:30:00Z"
}
```

### 6. List Uploaded Villages

```http
GET /api/data/villages

Response: 200 OK
{
  "villages": [
    {
      "village_id": "village_01",
      "name": "Chikkahullur",
      "source": "synthetic",
      "created_at": "2026-08-18T10:00:00Z"
    },
    {
      "village_id": "village_03",
      "name": "Dommasandra",
      "source": "user_upload",
      "created_at": "2026-08-20T15:30:00Z"
    }
  ],
  "count": 2
}
```

### 7. Delete Village

```http
DELETE /api/data/villages/{village_id}

Response: 200 OK
{
  "village_id": "village_03",
  "status": "deleted",
  "message": "Village and all associated data deleted"
}
```

---

## Data Validation Rules

### Required Layers
1. **boundary** (mandatory)
   - 1 polygon feature
   - Valid geometry (no self-intersections)
   - Area > 0

2. **buildings** (mandatory)
   - ≥1 polygon/point features
   - Within boundary
   - Required attributes: building_id, households (or default to 1)

3. **facilities** (recommended)
   - Point features
   - Required attributes: facility_id, facility_type
   - Valid types: water, waste, health, education, etc.

### Optional Layers
4. **parcels** - Land ownership data
5. **roads** - Road network
6. **water_bodies** - Water features
7. **households** (CSV) - Household demographics

### CRS Requirements
- Must detect CRS automatically
- Common CRS supported:
  - EPSG:4326 (WGS84) - preferred
  - EPSG:32643 (UTM Zone 43N - Karnataka)
  - EPSG:32644 (UTM Zone 44N)
- Transform to EPSG:4326 if different

### File Format Support
- **GeoJSON** (.geojson, .json) - preferred
- **Shapefile** (.shp + .shx + .dbf + .prj)
- **KML** (.kml) - Google Earth
- **CSV** (.csv) - for household data with lat/lon

### Size Limits
- Max file size: 100MB per file
- Max total upload: 500MB
- Max features per layer:
  - Buildings: 10,000
  - Parcels: 50,000
  - Roads: 5,000 segments

---

## Attribute Mapping

### Auto-Detection Heuristics

The system attempts to auto-map uploaded attributes to schema:

```python
ATTRIBUTE_PATTERNS = {
    "building_id": ["ID", "BLDG_ID", "BUILD_ID", "FID", "OBJECTID"],
    "households": ["HOUSEHOLDS", "HH", "HH_COUNT", "FAMILIES"],
    "facility_type": ["TYPE", "FACILITY_TYPE", "CATEGORY", "FAC_TYPE"],
    "parcel_type": ["TYPE", "LAND_USE", "PARCEL_TYPE", "USE_TYPE"],
    "owner_type": ["OWNER", "OWNERSHIP", "OWNER_TYPE"],
    "road_type": ["TYPE", "ROAD_TYPE", "ROAD_CLASS", "CLASS"],
}
```

### Manual Mapping Interface

If auto-detection fails or is incorrect, user can manually map:

```
Uploaded Field          →    System Field
─────────────────────────────────────────────
STRUCTURE_ID            →    building_id
NO_OF_FAMILIES          →    households
LATITUDE                →    (use for centroid)
LONGITUDE               →    (use for centroid)
```

---

## Frontend UI (Mockup)

### Upload Page

```
┌─────────────────────────────────────────────────────────┐
│  Data Manager - Upload New Village                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Step 1: Upload Files                                  │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Drag & drop files here or click to browse       │ │
│  │                                                   │ │
│  │  Accepted formats:                                │ │
│  │  • GeoJSON (.geojson)                            │ │
│  │  • Shapefile (.shp + .shx + .dbf + .prj)        │ │
│  │  • KML (.kml)                                    │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  Uploaded Files:                                       │
│  ✓ boundary.geojson (2.5MB)                           │
│  ✓ buildings.geojson (15.3MB)                         │
│  ✓ facilities.geojson (0.5MB)                         │
│  ✓ parcels.geojson (25.1MB)                           │
│                                                         │
│  [Cancel]                    [Validate & Continue →]  │
└─────────────────────────────────────────────────────────┘
```

### Validation Page

```
┌─────────────────────────────────────────────────────────┐
│  Step 2: Validation Results                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ✓ boundary.geojson                                    │
│    Format: GeoJSON, CRS: EPSG:32643, Features: 1      │
│                                                         │
│  ✓ buildings.geojson                                   │
│    Format: GeoJSON, CRS: EPSG:32643, Features: 250    │
│    ⚠ Warning: Missing 'households' field (will use 1) │
│                                                         │
│  ✓ facilities.geojson                                  │
│    Format: GeoJSON, CRS: EPSG:32643, Features: 5      │
│                                                         │
│  ✗ parcels.geojson                                     │
│    Format: GeoJSON, CRS: Unknown, Features: 500       │
│    ❌ Error: CRS not detected                          │
│    ❌ Error: 15 invalid geometries                     │
│                                                         │
│  Summary: 3 valid, 1 invalid                           │
│                                                         │
│  [← Back]  [Fix Errors]           [Continue Anyway →] │
└─────────────────────────────────────────────────────────┘
```

### Preview & Mapping Page

```
┌─────────────────────────────────────────────────────────┐
│  Step 3: Preview & Attribute Mapping                   │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────┬─────────────────────────┐ │
│  │  Map Preview            │  Attribute Mapping      │ │
│  │                         │                         │ │
│  │  [Interactive map       │  Layer: buildings       │ │
│  │   showing uploaded      │                         │ │
│  │   boundary + buildings] │  Uploaded → System      │ │
│  │                         │  ─────────────────────  │ │
│  │  Statistics:            │  ID → building_id       │ │
│  │  • Area: 250 hectares   │  NAME → building_name   │ │
│  │  • Buildings: 250       │  HH → households ✓      │ │
│  │  • Facilities: 5        │                         │ │
│  │                         │  [Auto-detect]          │ │
│  └─────────────────────────┴─────────────────────────┘ │
│                                                         │
│  [← Back]                          [Register Village →]│
└─────────────────────────────────────────────────────────┘
```

### Registration Page

```
┌─────────────────────────────────────────────────────────┐
│  Step 4: Village Registration                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Village Information:                                  │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Village Name*: [Dommasandra________________]     │ │
│  │  Taluk*:        [Anekal_____________________]     │ │
│  │  District*:     [Bangalore Rural____________]     │ │
│  │  State*:        [Karnataka__________________]     │ │
│  │  Population:    [1500_______________________]     │ │
│  │                                                   │ │
│  │  Data Source:   [User Upload________________]     │ │
│  │  Source Date:   [2024-08-20_________________]     │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  Data Quality:                                         │
│  ✓ Boundary: Complete                                 │
│  ✓ Buildings: 250 features                            │
│  ✓ Facilities: 5 features                             │
│  ⚠ Parcels: Excluded (validation failed)              │
│                                                         │
│  [← Back]                         [Register & Save →] │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 9.1: File Upload (2 days)
- File upload endpoint with multipart/form-data
- Temporary storage in uploads/ directory
- File format detection
- Size validation

### Phase 9.2: Validation (3 days)
- GeoJSON validator
- Shapefile parser (using fiona/geopandas)
- CRS detection (using pyproj)
- Geometry validation (using shapely)
- Schema compliance checking

### Phase 9.3: Transformation (2 days)
- CRS transformation (pyproj)
- Attribute mapping engine
- Auto-detection heuristics
- Data standardization

### Phase 9.4: Registration (2 days)
- Village registration endpoint
- File system operations (move from temp to data/)
- Village registry update
- Metadata generation

### Phase 9.5: Frontend UI (3 days)
- Multi-step upload wizard
- File drag-and-drop
- Validation results display
- Attribute mapping interface
- Preview map integration

**Total Estimated Time**: 12 days

---

## Technology Stack

### Backend
- **File Upload**: FastAPI multipart support
- **GIS Processing**: 
  - GeoPandas (Shapefile, GeoJSON)
  - Fiona (format conversion)
  - Shapely (geometry validation)
  - PyProj (CRS transformation)
- **Validation**: Custom validators + JSON Schema
- **Storage**: File system (data/villages/{id}/)

### Frontend
- **File Upload**: react-dropzone
- **Progress**: Upload progress bars
- **Validation Display**: Error/warning lists
- **Mapping Interface**: Drag-and-drop attribute mapper
- **Preview**: MapLibre GL JS integration

---

## Security Considerations

1. **File Type Validation**: Whitelist only .geojson, .shp, .kml, .csv
2. **Size Limits**: 100MB per file, 500MB total
3. **Virus Scanning**: Optional integration with ClamAV
4. **Path Traversal**: Sanitize filenames
5. **User Quotas**: Limit uploads per user (if auth added)
6. **Rate Limiting**: Max 5 uploads per hour

---

## Testing Strategy

### Unit Tests
- File validator (valid/invalid formats)
- CRS transformer (various CRS → EPSG:4326)
- Attribute mapper (auto-detection accuracy)
- Schema validator (compliance checking)

### Integration Tests
- Complete upload workflow
- Multi-file uploads
- Error handling (invalid files)
- Registration process

### Manual Testing
- Upload real Shapefile from SVAMITVA portal
- Upload various CRS formats
- Test with intentionally broken files
- Verify village appears in list and works with optimization

---

## Success Criteria

1. ✅ Upload GeoJSON files successfully
2. ✅ Upload Shapefile (.shp + companions) successfully
3. ✅ Detect and transform CRS automatically
4. ✅ Validate geometry and attributes
5. ✅ Map attributes with >80% auto-detection accuracy
6. ✅ Register village and make available for optimization
7. ✅ Complete workflow in < 5 minutes for typical village

---

## Known Limitations

1. **No Database**: Uses file system (sufficient for prototype)
2. **No Concurrent Uploads**: One upload at a time per user
3. **Limited Format Support**: No support for TAB, GeoPackage (yet)
4. **Manual Attribute Mapping**: If auto-detection fails
5. **No Versioning**: Overwriting data replaces original

---

## Future Enhancements (Post-Phase 9)

1. **Database Storage**: PostgreSQL + PostGIS for better scalability
2. **Version Control**: Track data changes over time
3. **Batch Upload**: Upload 10-100 villages at once
4. **Data Quality Scoring**: Automated quality assessment
5. **Integration APIs**: Direct connection to SVAMITVA portal
6. **ML-Powered Mapping**: Better attribute auto-detection
7. **Collaborative Editing**: Multi-user data management

---

## Conclusion

Phase 9 would enable PlanGram to work with real village data from any source. The multi-step upload workflow (upload → validate → transform → register) ensures data quality while remaining user-friendly.

**Priority Assessment**: 
- **Backend Complete**: Yes, 100%
- **Data Upload Need**: Medium (prototype has 2 villages)
- **Recommendation**: Implement Phase 10 (AI) or Phase 12 (Polish) first, then Phase 9 if real data uploads are needed.

**Status**: ✅ **SPECIFICATION COMPLETE**

This document serves as the complete design specification for Phase 9 implementation.

---

*PlanGram - Explore. Simulate. Plan.*  
*Phase 9 Specification: Data Manager for Custom Village Uploads*
