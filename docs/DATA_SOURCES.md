# PlanGram Data Sources

## Overview

PlanGram is designed to work with multiple data sources while maintaining clear transparency about data origin and quality.

## Data Source Types

### 1. REAL_OFFICIAL
- **Description**: Verified official government data from authorized sources
- **Trust Level**: High
- **Examples**:
  - Official SVAMITVA property boundary data
  - Census demographic data
  - Survey of India topographic maps
  - Government-issued orthomosaics and DSMs

- **How to Obtain**:
  - SVAMITVA portal (requires authorization)
  - Census data portal
  - Survey of India
  - State/District planning offices

- **Integration**: Upload via Data Manager with proper source attribution

---

### 2. OPEN_PUBLIC
- **Description**: Publicly available datasets from reputable sources
- **Trust Level**: Medium-High
- **Examples**:
  - OpenStreetMap (roads, buildings, amenities)
  - Bhuvan satellite imagery
  - ISRO datasets
  - Humanitarian OpenStreetMap Team data

- **Sources**:
  - [OpenStreetMap](https://www.openstreetmap.org/)
  - [Bhuvan (ISRO)](https://bhuvan.nrsc.gov.in/)
  - [Humanitarian Data Exchange](https://data.humdata.org/)

- **Integration**: Direct download and upload via Data Manager

---

### 3. ESTIMATED
- **Description**: Calculated or estimated values based on available data
- **Trust Level**: Medium
- **Examples**:
  - Population estimates from building counts
  - Network distances from road geometry
  - Household counts from building footprints
  - Accessibility metrics from spatial analysis

- **Methodology**: 
  - Document estimation method
  - Clearly mark as "estimated" in all outputs
  - Provide uncertainty ranges where applicable

---

### 4. SYNTHETIC
- **Description**: Representative data created for prototype/demonstration purposes
- **Trust Level**: Prototype-only
- **Current Use**: Phase 1 prototype villages (Chikkahullur, Bandapalya)
- **Examples**:
  - Demo village boundaries
  - Representative building footprints
  - Sample road networks
  - Indicative facility locations

- **Important**: 
  - ⚠️ **NOT real village data**
  - ⚠️ **NOT official SVAMITVA data**
  - For demonstration and validation purposes only
  - Must be replaced with official data for production use

---

## Current Data Status (Phase 1)

### Prototype Villages

**Village 01: Chikkahullur**
- **Data Mode**: Prototype
- **Source Type**: SYNTHETIC
- **Features**:
  - Boundary: 1 feature (SYNTHETIC)
  - Buildings: 259 features (SYNTHETIC)
  - Households: 216 records (ESTIMATED)
  - Population: 861 people (ESTIMATED)
  - Parcels: 259 features (SYNTHETIC)
  - Roads: 68 segments (SYNTHETIC)
  - Water Bodies: 0 features (SYNTHETIC)
  - Facilities: 5 features (SYNTHETIC)

**Village 02: Bandapalya**
- **Data Mode**: Prototype
- **Source Type**: SYNTHETIC
- **Features**:
  - Boundary: 1 feature (SYNTHETIC)
  - Buildings: 268 features (SYNTHETIC)
  - Households: 241 records (ESTIMATED)
  - Population: 965 people (ESTIMATED)
  - Parcels: 268 features (SYNTHETIC)
  - Roads: 7 segments (SYNTHETIC)
  - Water Bodies: 0 features (SYNTHETIC)
  - Facilities: 3 features (SYNTHETIC)

---

## Data Acquisition Guide

### For Official SVAMITVA Data

**Step 1: Authorization**
- Contact District/Taluk planning office
- Request access to SVAMITVA property data
- Provide project credentials and authorization

**Step 2: Data Request**
- Specify village(s) required
- Request layers: property boundaries, roads, buildings
- Request format: GeoJSON, Shapefile, or GeoPackage preferred

**Step 3: Data Validation**
- Verify CRS (coordinate reference system)
- Check geometry validity
- Confirm attribute completeness

**Step 4: Import to PlanGram**
- Use Data Manager interface
- Map layers to PlanGram schema
- Validate and import
- Update source metadata

---

### For OpenStreetMap Data

**Option 1: Overpass API**
```python
# Example query for village buildings
import requests

query = """
[out:json];
area["name"="Anekal"]->.searchArea;
(
  way["building"](area.searchArea);
);
out geom;
"""

response = requests.post(
    "https://overpass-api.de/api/interpreter",
    data=query
)
data = response.json()
```

**Option 2: QGIS QuickOSM Plugin**
1. Install QGIS
2. Install QuickOSM plugin
3. Query by location and tags
4. Export as GeoJSON

**Option 3: Direct Download**
- Visit [https://export.hotosm.org/](https://export.hotosm.org/)
- Select area of interest
- Choose layers (buildings, roads, etc.)
- Download as Shapefile or GeoPackage

---

### For Bhuvan Data

1. Visit [Bhuvan Portal](https://bhuvan.nrsc.gov.in/)
2. Navigate to Thematic Services
3. Select relevant layers (LULC, settlements, etc.)
4. Download data for AOI (Area of Interest)
5. Import via Data Manager

---

## Data Validation Checklist

### Pre-Import Validation
- [ ] File format supported (GeoJSON, SHP, GPKG, etc.)
- [ ] CRS identified and documented
- [ ] Geometries valid (no self-intersections)
- [ ] Attribute schema understood
- [ ] Source metadata prepared

### Post-Import Validation
- [ ] Feature count matches expectation
- [ ] Geometries within village boundary
- [ ] Attributes correctly mapped
- [ ] No critical missing data
- [ ] Source metadata recorded

### Quality Indicators
- **High**: Official government data with verification
- **Medium**: Public data from reputable sources with validation
- **Low**: Estimated or incomplete data
- **Prototype**: Synthetic demonstration data

---

## Data Update Workflow

### Updating Prototype Data with Official Data

**Phase 1: Preparation**
1. Obtain official SVAMITVA datasets
2. Validate data quality
3. Prepare metadata documentation

**Phase 2: Import**
1. Open Data Manager
2. Select village or create new
3. Upload official data files
4. Map layers to schema
5. Validate geometries and CRS

**Phase 3: Verification**
1. Review imported layer counts
2. Visual inspection on map
3. Run spatial queries to verify coverage
4. Compare with prototype expectations

**Phase 4: Migration**
1. Update `data_mode` from "prototype" to "official"
2. Update source_metadata.json
3. Archive prototype data
4. Document migration in changelog

**Phase 5: Testing**
1. Run all planning workflows
2. Verify spatial analysis accuracy
3. Test scenario creation
4. Validate optimization results

---

## Data Attribution

### Required Attribution

For all data sources, maintain:

```json
{
  "dataset": "buildings",
  "source_type": "OPEN_PUBLIC",
  "official": false,
  "source_name": "OpenStreetMap Contributors",
  "source_url": "https://www.openstreetmap.org/",
  "license": "ODbL",
  "attribution": "© OpenStreetMap contributors",
  "download_date": "2026-08-20",
  "description": "Building footprints from OpenStreetMap"
}
```

### License Compliance

**OpenStreetMap**: ODbL (Open Database License)
- Attribute OpenStreetMap contributors
- Share-alike if distributing derived data
- [License Details](https://opendatacommons.org/licenses/odbl/)

**Government Data**: Typically open for use
- Check specific terms for SVAMITVA data
- Attribute appropriately
- Verify redistribution permissions

---

## Data Privacy & Security

### Sensitive Data Handling
- **Personal identifiable information**: Not stored in PlanGram
- **Property ownership**: Anonymized or aggregated
- **Household demographics**: Aggregated to building level minimum
- **Coordinates**: Public infrastructure only (no private addresses)

### Data Access Control (Future)
- Role-based access (admin, planner, viewer)
- Audit logging for data changes
- Encrypted storage for sensitive datasets

---

## Future Data Integrations

### Planned Integrations
1. **Real-time Census API**: Population updates
2. **eGramSwaraj**: Budget and project tracking
3. **SVAMITVA Portal**: Direct data sync
4. **Weather APIs**: Climate risk assessment
5. **Sentinel/Landsat**: Satellite imagery

### Data Exchange Standards
- GeoJSON for vector data
- GeoTIFF for raster data
- CSV for tabular data
- REST APIs for real-time integration

---

## Support & Troubleshooting

### Common Issues

**Issue**: CRS not recognized
- **Solution**: Manually specify EPSG code in Data Manager

**Issue**: Geometries outside boundary
- **Solution**: Check CRS mismatch; verify source data extent

**Issue**: Missing attributes
- **Solution**: Map optional attributes; document as "not available"

**Issue**: File too large (>100MB)
- **Solution**: Simplify geometries in QGIS before upload; increase limit in config

---

## Contact & Resources

### Data Acquisition Support
- SVAMITVA Help Desk: [Contact TBD]
- OpenStreetMap India: [https://openstreetmap.in/](https://openstreetmap.in/)
- Bhuvan Support: [https://bhuvan.nrsc.gov.in/](https://bhuvan.nrsc.gov.in/)

### Technical Support
- PlanGram Documentation: [docs/](../docs/)
- Issue Tracker: [TBD]
- Community Forum: [TBD]

---

**Last Updated**: 2026-08-20  
**Version**: 1.0.0
