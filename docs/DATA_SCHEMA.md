# PlanGram Data Schema

## Overview

PlanGram uses a common spatial data model that remains consistent regardless of data source (synthetic, uploaded, or official).

## Core Entities

### 1. Village

**Purpose**: Administrative boundary and container for all spatial data

**Attributes**:
- `id` (string): Unique village identifier (e.g., "village_01")
- `name` (string): Human-readable village name
- `taluk` (string): Taluk/block name
- `district` (string): District name
- `state` (string): State name
- `data_mode` (enum): "prototype" | "uploaded" | "official"
- `area_sq_km` (float): Village area in square kilometers
- `estimated_population` (integer): Total population (may be estimated)
- `estimated_households` (integer): Total households (may be estimated)
- `geometry` (Polygon): Village boundary (EPSG:4326)
- `metadata` (JSON): Additional metadata including data sources

**Files**:
- `data/villages/{village_id}/boundary.geojson`

---

### 2. Building

**Purpose**: Individual building footprints

**Attributes**:
- `building_id` (string): Unique identifier
- `village_id` (string): Foreign key to village
- `building_type` (enum): "residential" | "commercial" | "public" | "agricultural" | "other"
- `estimated_households` (integer): Households in this building
- `estimated_population` (integer): Population in this building
- `area_sq_m` (float): Building footprint area
- `geometry` (Polygon): Building footprint (EPSG:4326)

**Files**:
- `data/villages/{village_id}/buildings.geojson`

**GeoJSON Example**:
```json
{
  "type": "Feature",
  "properties": {
    "building_id": "bldg_001",
    "building_type": "residential",
    "estimated_households": 1,
    "estimated_population": 4,
    "area_sq_m": 85.3
  },
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[77.123, 12.456], ...]]
  }
}
```

---

### 3. Parcel

**Purpose**: Land parcel boundaries

**Attributes**:
- `parcel_id` (string): Unique identifier
- `village_id` (string): Foreign key to village
- `parcel_type` (enum): "residential" | "commercial" | "agricultural" | "public" | "vacant" | "other"
- `owner_type` (enum): "private" | "government" | "common" | "unknown"
- `area_sq_m` (float): Parcel area
- `restricted` (boolean): Whether parcel has development restrictions
- `geometry` (Polygon): Parcel boundary (EPSG:4326)

**Files**:
- `data/villages/{village_id}/parcels.geojson`

---

### 4. Road

**Purpose**: Road network for distance calculations and accessibility

**Attributes**:
- `road_id` (string): Unique identifier
- `village_id` (string): Foreign key to village
- `road_type` (enum): "highway" | "main" | "local" | "path"
- `surface` (enum): "paved" | "unpaved" | "unknown"
- `length_m` (float): Road segment length in meters
- `geometry` (LineString): Road centerline (EPSG:4326)

**Files**:
- `data/villages/{village_id}/roads.geojson`

---

### 5. Water Body

**Purpose**: Natural water features (constraints for infrastructure placement)

**Attributes**:
- `waterbody_id` (string): Unique identifier
- `village_id` (string): Foreign key to village
- `waterbody_type` (enum): "tank" | "pond" | "lake" | "canal" | "river" | "well"
- `seasonal` (boolean): Whether water body is seasonal
- `area_sq_m` (float): Water body area
- `geometry` (Polygon): Water body boundary (EPSG:4326)

**Files**:
- `data/villages/{village_id}/water_bodies.geojson`

---

### 6. Facility

**Purpose**: Existing infrastructure facilities

**Attributes**:
- `facility_id` (string): Unique identifier
- `village_id` (string): Foreign key to village
- `facility_type` (enum): "water" | "waste" | "health" | "education" | "public_toilet" | "bus_stop" | "other"
- `name` (string): Facility name
- `status` (enum): "existing" | "proposed" | "under_construction" | "deprecated"
- `capacity` (integer, optional): Service capacity (type-dependent)
- `cost` (float, optional): Construction/upgrade cost
- `year_established` (integer, optional)
- `geometry` (Point): Facility location (EPSG:4326)

**Files**:
- `data/villages/{village_id}/facilities.geojson`

**GeoJSON Example**:
```json
{
  "type": "Feature",
  "properties": {
    "facility_id": "fac_water_001",
    "facility_type": "water",
    "name": "Community Water Point - North",
    "status": "existing",
    "capacity": 150,
    "year_established": 2018
  },
  "geometry": {
    "type": "Point",
    "coordinates": [77.123, 12.456]
  }
}
```

---

### 7. Household

**Purpose**: Household-level demographic data

**Attributes**:
- `household_id` (string): Unique identifier
- `building_id` (string): Foreign key to building
- `village_id` (string): Foreign key to village
- `estimated_population` (integer): People in household
- `estimated` (boolean): Whether data is estimated vs. official
- `income_category` (enum, optional): "low" | "medium" | "high" | "unknown"
- `priority_category` (enum, optional): "high" | "medium" | "low"

**Files**:
- `data/villages/{village_id}/households.csv`

**CSV Example**:
```csv
household_id,building_id,estimated_population,estimated
hh_001,bldg_001,4,true
hh_002,bldg_002,3,true
```

---

### 8. Scenario

**Purpose**: Saved planning scenarios with proposed infrastructure

**Attributes**:
- `scenario_id` (string): Unique identifier
- `village_id` (string): Foreign key to village
- `name` (string): Scenario name
- `description` (string): User-provided description
- `budget` (float): Total budget constraint
- `created_at` (datetime)
- `created_by` (string, optional): User identifier

**Related Entity**: Scenario Project

---

### 9. Scenario Project

**Purpose**: Individual infrastructure projects within a scenario

**Attributes**:
- `project_id` (string): Unique identifier
- `scenario_id` (string): Foreign key to scenario
- `facility_type` (enum): Infrastructure type
- `cost` (float): Project cost
- `geometry` (Point): Proposed location (EPSG:4326)
- `impact_metrics` (JSON): Calculated impact (households served, coverage, etc.)

---

### 10. Dataset

**Purpose**: Track uploaded/imported datasets

**Attributes**:
- `dataset_id` (string): Unique identifier
- `village_id` (string): Foreign key to village
- `source_type` (enum): "REAL_OFFICIAL" | "OPEN_PUBLIC" | "ESTIMATED" | "SYNTHETIC"
- `source_name` (string): Source description
- `upload_date` (datetime)
- `uploaded_by` (string, optional)
- `file_path` (string): Original file location
- `original_crs` (string): Original coordinate reference system
- `status` (enum): "uploaded" | "validated" | "imported" | "failed"

**Related Entity**: Dataset Layer

---

### 11. Dataset Layer

**Purpose**: Individual layers within an uploaded dataset

**Attributes**:
- `layer_id` (string): Unique identifier
- `dataset_id` (string): Foreign key to dataset
- `layer_name` (string): Layer name from upload
- `mapped_to` (enum): Target PlanGram entity ("buildings", "parcels", etc.)
- `geometry_type` (string): "Point", "LineString", "Polygon"
- `feature_count` (integer)
- `crs` (string)

---

## Coordinate Reference System (CRS)

**Internal CRS**: EPSG:4326 (WGS 84)

**Rationale**:
- Compatible with web mapping libraries (MapLibre GL JS)
- Widely used for GPS data
- Supports global extent

**Handling**:
- All uploaded data is converted to EPSG:4326
- Original CRS is preserved in metadata
- Distance calculations may use local UTM projection internally for accuracy

---

## Data Validation Rules

### Building
- Must be within village boundary
- `estimated_households` >= 0
- `estimated_population` >= 0
- Polygon must be valid (no self-intersections)

### Parcel
- Must be within village boundary
- Polygon must be valid
- `area_sq_m` > 0

### Road
- LineString must be valid
- `length_m` > 0

### Facility
- Must be within village boundary (with small tolerance)
- Point must be valid
- Cost must be >= 0 if provided

### Household
- Must reference valid building_id
- `estimated_population` >= 0

---

## Metadata Schema

Every dataset includes metadata:

```json
{
  "dataset": "buildings",
  "source_type": "SYNTHETIC",
  "official": false,
  "source_name": "PlanGram representative prototype dataset",
  "description": "Representative building footprints used for prototype validation",
  "geometry_type": "Polygon",
  "crs": "EPSG:4326",
  "feature_count": 720,
  "created_at": "2026-08-20",
  "attributes": ["building_id", "building_type", "estimated_households", "estimated_population"]
}
```

---

## Database Schema (PostgreSQL + PostGIS)

### Table: villages
```sql
CREATE TABLE villages (
  id VARCHAR PRIMARY KEY,
  name VARCHAR NOT NULL,
  taluk VARCHAR,
  district VARCHAR,
  state VARCHAR,
  data_mode VARCHAR CHECK (data_mode IN ('prototype', 'uploaded', 'official')),
  area_sq_km FLOAT,
  estimated_population INTEGER,
  estimated_households INTEGER,
  geometry GEOMETRY(Polygon, 4326),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_villages_geometry ON villages USING GIST(geometry);
```

### Table: buildings
```sql
CREATE TABLE buildings (
  building_id VARCHAR PRIMARY KEY,
  village_id VARCHAR REFERENCES villages(id),
  building_type VARCHAR,
  estimated_households INTEGER,
  estimated_population INTEGER,
  area_sq_m FLOAT,
  geometry GEOMETRY(Polygon, 4326),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_buildings_village ON buildings(village_id);
CREATE INDEX idx_buildings_geometry ON buildings USING GIST(geometry);
```

### Table: facilities
```sql
CREATE TABLE facilities (
  facility_id VARCHAR PRIMARY KEY,
  village_id VARCHAR REFERENCES villages(id),
  facility_type VARCHAR,
  name VARCHAR,
  status VARCHAR DEFAULT 'existing',
  capacity INTEGER,
  cost FLOAT,
  year_established INTEGER,
  geometry GEOMETRY(Point, 4326),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_facilities_village ON facilities(village_id);
CREATE INDEX idx_facilities_geometry ON facilities USING GIST(geometry);
CREATE INDEX idx_facilities_type ON facilities(facility_type);
```

(Additional tables follow similar patterns)

---

## File Format Standards

### GeoJSON
- Must conform to RFC 7946
- Use EPSG:4326 coordinates
- Feature properties must match schema
- Avoid unnecessary precision (6 decimal places sufficient)

### CSV
- UTF-8 encoding
- Comma-separated
- Header row required
- Quote strings containing commas

### Shapefile
- Must include .shp, .shx, .dbf, .prj files
- Column names <= 10 characters
- Upload as ZIP archive

---

## Extensibility

### Adding New Infrastructure Types

1. Add to `facility_type` enum
2. Add cost entry to `data/cost_config.json`
3. Define type-specific constraints (optional)
4. No code changes required

### Adding New Villages

1. Create directory: `data/villages/{village_id}/`
2. Add entry to `data/village_registry.json`
3. Add GeoJSON/CSV files following schema
4. Update `data/source_metadata.json`
5. System automatically recognizes new village

---

**Version**: 1.0.0  
**Last Updated**: 2026-08-20
