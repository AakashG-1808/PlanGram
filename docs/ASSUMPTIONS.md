# PlanGram Assumptions & Limitations

## Data Assumptions

### Population & Demographics
- **Household size**: Average 3.5-4.5 people per household
- **Population estimates**: Derived from building counts and regional averages
- **Income distribution**: Not included in prototype (future enhancement)
- **Seasonal migration**: Not accounted for in static population figures

### Spatial Data
- **Building footprints**: Residential buildings assumed to be single-household unless indicated
- **Road network**: Assumed to be traversable year-round
- **Water bodies**: Treated as static (seasonal variations not modeled)
- **Parcel ownership**: Simplified categories; actual land tenure may be complex

### Infrastructure Access
- **Water facility threshold**: Default 500 meters (configurable)
  - Rationale: Based on WHO/UNICEF guidelines for rural water access
  - Households within 500m considered "served"
  - Distance measured as network distance where road data available, otherwise straight-line

- **Service capacity**: Water facility serves ~100-150 households
  - Assumption: Single community tap with adequate flow rate
  - Actual capacity depends on water source, storage, and distribution design

### Cost Estimates
- **All costs are INDICATIVE for planning purposes only**
- **NOT official government procurement rates**
- Cost assumptions:
  - Water facility: ₹1,80,000 base cost
  - Does not include land acquisition
  - Assumes reasonable site accessibility
  - Excludes professional fees and administrative overhead
  - Based on 2026 estimates for Karnataka rural context

- **Maintenance costs**: Provided as annual estimates, exclude operational staff

## Technical Assumptions

### GIS & Spatial Analysis
- **Coordinate System**: All data converted to EPSG:4326 for web compatibility
- **Distance calculations**: 
  - Network distance preferred when road data available
  - Euclidean (straight-line) distance as fallback
  - Network routing assumes roads are bidirectional and accessible
  
- **Coverage calculation**: Binary threshold-based
  - Household is either "served" or "underserved"
  - Gradient-based accessibility metrics (future enhancement)

### Optimization
- **Single-objective optimization**: Currently maximizes weighted impact score
- **Budget constraint**: Hard constraint (cannot exceed)
- **Weights**: Configurable but use default values if not specified
  - Population benefit: 40%
  - Accessibility improvement: 25%
  - Underserved households: 20%
  - Cost efficiency: 10%
  - Environmental suitability: 5%

- **Optimization timeout**: 60 seconds default
- **Solution quality**: Returns best solution found within timeout (may not be globally optimal)

### AI & Insights
- **AI role**: Natural language interpretation and explanation generation only
- **AI does NOT calculate**: distances, coverage, geometry, scores, budgets
- **All numerical results**: Deterministic GIS calculations
- **AI failure mode**: System continues with deterministic results if AI unavailable

## Prototype Synthetic Data

### Village 01 (Chikkahullur)
- **Pattern**: Clustered settlements with central facilities
- **Challenge**: Eastern area underserved
- **Characteristics**: Moderate density, good road connectivity

### Village 02 (Bandapalya)
- **Pattern**: Dispersed settlements with limited central facilities
- **Challenge**: Multiple underserved pockets
- **Characteristics**: Lower density, limited road network

### Data Generation
- **Deterministic**: Uses fixed random seed for reproducibility
- **Realistic clustering**: Settlement patterns reflect typical rural Karnataka geography
- **Road-connected**: Buildings placed near roads where possible
- **Topological validity**: All geometries are valid (no self-intersections)

## System Limitations

### Current Prototype Limitations
1. **Two villages only**: Designed for 2 villages in Phase 1
2. **Single infrastructure type**: Water facilities fully implemented
3. **No terrain analysis**: Elevation, slope not considered
4. **Static data**: No real-time updates or temporal analysis
5. **No user authentication**: Single-user system
6. **No mobile optimization**: Desktop-first design
7. **Limited offline support**: Requires internet connection

### Data Ingestion Limitations
1. **File size**: Uploads limited to 100MB default
2. **Format support**: Vector and raster formats as documented
3. **CRS support**: Common CRS (WGS84, UTM) well-supported; obscure CRS may require manual intervention
4. **Attribute mapping**: User must manually map uploaded layer attributes

### Optimization Limitations
1. **Single-objective**: Multi-objective Pareto optimization not implemented
2. **Infrastructure interactions**: Does not model synergies between different infrastructure types
3. **Phasing**: Does not optimize multi-year implementation schedules
4. **Uncertainty**: Does not model population growth or demand uncertainty

### AI Limitations
1. **API dependency**: Requires Gemini API key for AI features
2. **Language support**: Currently English-optimized
3. **Domain knowledge**: General-purpose model, not fine-tuned for rural planning
4. **Hallucination risk**: AI explanations grounded in calculated metrics to minimize risk

## Planning Limitations

### Decision-Making
- **PlanGram is a decision-support tool, not a decision-maker**
- Final planning decisions remain with authorized Panchayat officials
- System recommendations should be reviewed by domain experts
- Tool outputs should be validated with local knowledge

### Validation Requirements
- **Community consultation**: Not replaced by PlanGram
- **Site visits**: Essential for validation
- **Stakeholder input**: Required for equitable planning
- **Regulatory compliance**: Must be verified independently

### Not Modeled
- **Political boundaries**: Ward-level or below
- **Social factors**: Caste, religion, community dynamics
- **Land tenure complexity**: Informal settlements, disputed land
- **Regulatory constraints**: Setbacks, zoning beyond basic rules
- **Environmental impact**: Detailed EIA not included
- **Cultural sites**: Heritage or religious site protection

## Data Privacy & Security

### Current Status
- **No personal data**: Household data is aggregated/anonymous
- **No authentication**: Single-user prototype
- **Local storage**: Data stored locally, not shared
- **No tracking**: No user analytics or tracking

### Production Requirements (Future)
- Role-based access control
- Audit logging
- Data encryption at rest and in transit
- Personal data protection compliance
- Secure API authentication

## Cost-Benefit Analysis Limitations

### Not Included
- **Economic benefits**: Revenue, productivity gains not quantified
- **Social benefits**: Health, education outcomes not monetized
- **Environmental benefits**: Ecosystem services not valued
- **Indirect costs**: Land use opportunity costs not included
- **Risk assessment**: Natural disasters, climate change impacts not modeled

## Validation & Testing

### Testing Scope
- **Spatial calculations**: Validated with known test cases
- **Optimization**: Validated for mathematical correctness
- **UI/UX**: User testing with planning officials recommended
- **Accessibility compliance**: WCAG validation requires expert review

### Not Tested
- **Large-scale performance**: Beyond 2-5 villages
- **Concurrent users**: Multi-user scenarios
- **Real SVAMITVA data**: Actual format variations
- **All edge cases**: Unusual geometries, data quality issues

## Integration Assumptions

### Current State
- **Standalone system**: Not integrated with other government platforms
- **Manual data entry**: Scenario results must be exported manually

### Future Integration Possibilities
- eGramSwaraj integration
- SVAMITVA property data portal
- State/district planning systems
- Budget management systems

## Regulatory & Compliance

### Important Disclaimers
1. **Not a substitute for professional planning advice**
2. **Cost estimates are indicative, not official procurement rates**
3. **Population data is estimated for prototype purposes**
4. **Synthetic data does NOT represent actual village conditions**
5. **Infrastructure recommendations require validation by qualified engineers**
6. **Land use decisions must comply with applicable regulations**
7. **Environmental clearances must be obtained independently**

## Future Enhancements

### Planned Improvements
- Multi-infrastructure optimization
- Temporal planning (multi-year)
- Uncertainty modeling
- Mobile-responsive design
- Offline capability
- Regional language support
- Advanced constraint modeling

### Research Areas
- Machine learning for infrastructure priority prediction
- Agent-based modeling for demand projection
- Network optimization for connected infrastructure
- Climate resilience scenarios

---

## Using PlanGram Responsibly

**DO**:
- Use for scenario exploration and comparison
- Validate recommendations with local knowledge
- Consult with communities and stakeholders
- Verify cost estimates with procurement data
- Conduct site visits for selected locations
- Document planning rationale

**DON'T**:
- Claim synthetic data is official government data
- Make final decisions based solely on tool output
- Skip community consultation
- Ignore local context and constraints
- Use cost estimates for actual procurement
- Deploy infrastructure without proper engineering review

---

**Last Updated**: 2026-08-20  
**Version**: 1.0.0
