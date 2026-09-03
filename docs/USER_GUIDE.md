# PlanGram User Guide

**Version**: 1.0.0  
**Last Updated**: August 20, 2026

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Understanding the Interface](#understanding-the-interface)
4. [Running Coverage Analysis](#running-coverage-analysis)
5. [Generating Candidate Locations](#generating-candidate-locations)
6. [Optimizing Infrastructure Placement](#optimizing-infrastructure-placement)
7. [Using AI Features](#using-ai-features)
8. [Interpreting Results](#interpreting-results)
9. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is PlanGram?

PlanGram is an **Interactive Spatial Decision Support System** for rural infrastructure planning. It helps village planners and decision-makers answer:

- **Where** should infrastructure be placed for maximum impact?
- **How many** facilities are needed within budget?
- **Which locations** meet all constraints and requirements?
- **What impact** will proposed placements have on coverage?

### Who is this for?

- Village planners and administrators
- Infrastructure development agencies
- Government officials managing rural development
- NGOs working on rural infrastructure
- Technical consultants

### Key Features

✅ **Coverage Analysis**: Identify underserved areas  
✅ **Constraint Validation**: Check location suitability  
✅ **Candidate Generation**: Find optimal placement locations  
✅ **Budget Optimization**: Maximize impact within budget  
✅ **AI Assistance**: Natural language queries and explanations  
✅ **Scenario Comparison**: Evaluate multiple options  

---

## Getting Started

### System Requirements

**Minimum**:
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- Screen resolution: 1280x720 or higher

**Recommended**:
- Chrome or Firefox (latest version)
- 1920x1080 resolution
- 4GB RAM

### Accessing PlanGram

1. Open your web browser
2. Navigate to: `http://your-plangram-url.com`
3. The application loads automatically (no login required in prototype mode)

### First Time Setup

No setup required! PlanGram comes pre-loaded with:
- 2 representative villages (Chikkahullur, Bandapalya)
- Complete GIS data (buildings, facilities, roads, water bodies)
- Cost configurations for infrastructure types

---

## Understanding the Interface

### Main Components

```
┌─────────────────────────────────────────────────┐
│  Header: PlanGram Logo + Navigation             │
├─────────────────────┬───────────────────────────┤
│                     │                           │
│  Sidebar:           │  Map View:                │
│  - Village Selector │  - Interactive Map        │
│  - Metrics Panel    │  - Layer Controls         │
│  - Tools Panel      │  - Zoom Controls          │
│  - Insights         │  - Legend                 │
│                     │                           │
└─────────────────────┴───────────────────────────┘
```

### Village Selector

**Location**: Top of sidebar

**Purpose**: Choose which village to analyze

**How to use**:
1. Click the dropdown
2. Select a village (e.g., "Chikkahullur")
3. Map automatically centers on selected village

### Metrics Panel

**Shows**:
- Current infrastructure coverage %
- Total buildings in village
- Buildings served/unserved
- Underserved clusters count

### Map Layers

**Available Layers**:
- 🗺️ **Boundary**: Village boundary polygon
- 🏠 **Buildings**: All structures in village
- 📦 **Parcels**: Land ownership parcels
- 🛣️ **Roads**: Road network
- 💧 **Water Bodies**: Rivers, ponds, lakes
- 🏢 **Facilities**: Existing infrastructure

**Toggle Layers**: Click layer names in Layer Controls panel

---

## Running Coverage Analysis

### What is Coverage Analysis?

Coverage analysis identifies which areas have good infrastructure access and which are underserved.

### Step-by-Step

1. **Select Village**
   - Choose village from dropdown

2. **Set Distance Threshold**
   - Use slider to set "access distance" (default: 500m)
   - 500m = building within 500m of facility is "served"

3. **View Results**
   - **Coverage %**: Percentage of buildings served
   - **Served Buildings**: Count of buildings with access
   - **Underserved Clusters**: Groups of buildings lacking access

4. **Interpret Color Coding**
   - 🟢 Green: Good coverage (>70%)
   - 🟡 Yellow: Moderate coverage (50-70%)
   - 🔴 Red: Poor coverage (<50%)

### Example

**Village**: Chikkahullur  
**Threshold**: 500m  
**Results**:
- Coverage: 59.3%
- Served: 154 buildings
- Unserved: 105 buildings
- Clusters: 6 underserved areas

**Interpretation**: Village has moderate coverage with 6 priority areas needing facilities.

---

## Generating Candidate Locations

### What are Candidates?

Candidate locations are computer-generated suggestions for where to place new infrastructure.

### Generation Methods

1. **Grid Method**: Samples locations evenly across village
2. **Gap Method**: Focuses on underserved areas
3. **Hybrid Method** (recommended): Combines both approaches

### Step-by-Step

1. **Open Candidate Generator**
   - Click "Generate Candidates" button

2. **Set Parameters**
   - Infrastructure type: water/waste/health/education
   - Number of candidates: 10-30 (default: 20)
   - Method: Hybrid (recommended)
   - Threshold: 500m (default)

3. **Generate**
   - Click "Generate"
   - Wait 2-5 seconds for results

4. **Review Candidates**
   - Candidates appear as markers on map
   - Each has a score (0-100)
   - Click marker to see details

### Understanding Scores

- **95-100**: Excellent - Highly recommended
- **85-94**: Very Good - Strong candidate
- **70-84**: Good - Suitable option
- **50-69**: Fair - Consider alternatives
- **<50**: Poor - Not recommended

### Score Factors

Scores consider:
- **Coverage Impact** (60% weight): Buildings served
- **Suitability** (40% weight): Constraints, land type, accessibility

---

## Optimizing Infrastructure Placement

### What is Optimization?

Optimization finds the best combination of facility locations to maximize coverage within your budget.

### Step-by-Step

1. **Set Budget**
   - Enter total budget (e.g., ₹300,000)
   - Cost per facility shown (e.g., ₹180,000)

2. **Choose Infrastructure Type**
   - Water, waste, health, or education

3. **Run Optimization**
   - Click "Optimize"
   - Wait 5-15 seconds

4. **Review Results**
   - **Selected Locations**: Optimal placement spots
   - **Coverage Improvement**: Increase in coverage %
   - **Buildings Served**: Number of new buildings served
   - **Cost**: Total cost and per-building cost
   - **Budget Utilization**: Percentage of budget used

### Budget Scenarios

**Feature**: Compare conservative, moderate, and aggressive budget levels

**How to use**:
1. Click "Compare Scenarios"
2. Enter base budget
3. System generates 3 scenarios:
   - Conservative: 70% of budget
   - Moderate: 100% of budget
   - Aggressive: 130% of budget

4. Review comparison table showing:
   - Facilities count
   - Coverage improvement
   - Cost efficiency (₹ per building)
   - Recommendation

### Example

**Budget**: ₹360,000  
**Result**:
- 2 facilities selected
- Coverage: 59.3% → 100% (+40.7%)
- Buildings served: +107
- Cost efficiency: ₹3,429 per building
- Budget used: 100%

---

## Using AI Features

### Natural Language Queries

**What it does**: Ask questions in plain English instead of clicking buttons

**Examples**:
```
"Find best water facility location in village_01 with budget 200000"
→ Runs optimization automatically

"Analyze coverage in village_02"
→ Runs coverage analysis

"Generate 20 candidates for water using hybrid method"
→ Generates candidates

"Compare scenarios for village_01"
→ Shows budget scenarios
```

**How to use**:
1. Find search bar at top
2. Type your question in natural language
3. Press Enter
4. System interprets and executes

### Recommendation Explanations

**What it does**: Explains WHY a location is recommended

**How to use**:
1. Click any candidate location or optimized placement
2. Click "Explain" button
3. Read detailed explanation with:
   - Summary (why this location)
   - Coverage impact
   - Constraint compliance
   - Cost efficiency
   - Warnings (if any)

**Example Explanation**:
```
This location scores 97.5/100 (Excellent), serving 92 buildings 
and improving coverage by 35.5%.

Key Factors:
1. Coverage Impact (98/100): Serves 92 underserved buildings
2. Constraint Compliance (97/100): Public land, 50m from road

Warnings: None

Alternatives: 2 other locations score 95+ within 200m
```

### Insights Generation

**What it does**: Automatically identifies key findings and recommendations

**How to use**:
1. Run coverage analysis
2. Click "Generate Insights"
3. Review 3-5 actionable insights categorized as:
   - 🔴 Critical: Urgent issues
   - 🟢 Opportunity: High-impact options
   - 🟡 Warning: Risks to be aware of

**Example Insights**:
```
Critical: "Significant Coverage Gaps Detected"
→ Action: Develop multi-facility plan for 80%+ coverage

Opportunity: "Large Underserved Cluster Identified"
→ Action: Prioritize placement near 78-building cluster

Warning: "Fragmented Coverage Pattern"
→ Action: Plan multi-phase implementation
```

---

## Interpreting Results

### Coverage Metrics

**Coverage %**: Percentage of buildings within threshold distance of a facility
- <40%: Critical - Immediate action needed
- 40-60%: Significant gaps - Priority for expansion
- 60-80%: Moderate - Targeted improvements
- >80%: Good - Address remaining gaps

**Underserved Clusters**: Groups of buildings lacking access
- More clusters = More dispersed needs
- Larger clusters = More impact per facility

### Constraint Violations

**Types**:
- ❌ **Critical**: Must not proceed (e.g., outside boundary)
- ⚠️ **Warning**: Proceed with caution (e.g., near water body)

**Common Violations**:
- Outside village boundary
- On private/restricted land
- Too close to water body (<10m critical, <30m warning)
- Poor road access (>200m)

### Cost Efficiency

**Cost per Building**: Total cost ÷ Buildings served

**Benchmarks**:
- <₹2,000: Excellent efficiency
- ₹2,000-₹4,000: Good efficiency
- ₹4,000-₹6,000: Moderate efficiency
- >₹6,000: High cost - verify benefits

### Optimization Results

**Diminishing Returns**: When adding facilities yields less improvement

**Example**:
- Facility 1: +35% coverage (₹1,957/building)
- Facility 2: +6% coverage (₹5,047/building) ← Diminishing returns
- Facility 3: +0.5% coverage (₹18,000/building) ← Not worth it

**Recommendation**: Stop when cost efficiency drops significantly

---

## Troubleshooting

### Common Issues

#### 1. Map Not Loading

**Symptoms**: Blank map area, spinning loader

**Solutions**:
- Check internet connection
- Refresh page (F5 or Ctrl+R)
- Clear browser cache
- Try different browser

#### 2. Village Data Not Found

**Symptoms**: "Village not found" error

**Solutions**:
- Verify village ID is correct (village_01 or village_02)
- Check that data files exist in `data/villages/`
- Contact administrator if problem persists

#### 3. Optimization Takes Too Long

**Symptoms**: Optimization running >60 seconds

**Solutions**:
- Reduce number of candidates (try 20 instead of 30)
- Use hybrid method instead of grid method
- Refresh and try again
- Contact support if timeout persists

#### 4. AI Features Not Working

**Symptoms**: "AI service unavailable" message

**Solutions**:
- This is normal if API key not configured
- System falls back to basic features
- All core features still work
- Contact administrator to enable AI

#### 5. "No Candidates Found"

**Symptoms**: Candidate generation returns 0 results

**Solutions**:
- Check that village has buildings data
- Try different generation method
- Adjust threshold (try 500m or 750m)
- Verify constraint settings aren't too strict

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| VILLAGE_NOT_FOUND | Village doesn't exist | Check village ID |
| INVALID_LOCATION | Coordinates invalid | Use map to select location |
| INSUFFICIENT_BUDGET | Budget too low | Increase budget or reduce facilities |
| NO_CANDIDATES_FOUND | No suitable locations | Adjust constraints or threshold |
| OPTIMIZATION_FAILED | Can't find solution | Increase budget or adjust parameters |

### Getting Help

**Documentation**: Check `/docs` folder for technical guides

**API Documentation**: Visit `http://localhost:8000/api/docs` for API reference

**Support**: Contact your system administrator or technical support team

---

## Tips & Best Practices

### For Best Results

1. **Start with Coverage Analysis**: Understand current state before optimizing
2. **Use Hybrid Method**: Best balance of coverage and suitability
3. **Check Constraints**: Review warnings before finalizing placement
4. **Compare Scenarios**: Don't optimize for just one budget level
5. **Review Explanations**: Understand WHY locations are recommended
6. **Watch for Diminishing Returns**: Stop adding facilities when efficiency drops

### Common Workflows

**Workflow 1: Find Optimal Placement**
1. Select village
2. Run coverage analysis
3. Generate insights
4. Set budget
5. Run optimization
6. Review explanations
7. Make decision

**Workflow 2: Evaluate Specific Location**
1. Select village
2. Click location on map
3. Click "Validate Location"
4. Review constraint compliance
5. Check coverage impact
6. Read AI explanation

**Workflow 3: Budget Planning**
1. Select village
2. Run coverage analysis
3. Click "Compare Scenarios"
4. Enter budget range
5. Review cost-benefit tradeoffs
6. Choose optimal scenario

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl/Cmd + F` | Focus search bar |
| `Ctrl/Cmd + M` | Toggle map layers |
| `Ctrl/Cmd + +` | Zoom in |
| `Ctrl/Cmd + -` | Zoom out |
| `Escape` | Close modals/panels |
| `F5` | Refresh page |

---

## Data Disclaimer

⚠️ **Important**: Current version uses representative **synthetic data** for demonstration purposes. This is NOT official SVAMITVA or government data.

All cost estimates are **indicative** for planning purposes only. Actual costs may vary based on local conditions, materials, labor, and other factors.

Final infrastructure decisions must be made by authorized officials following proper procedures and regulations.

---

## Version History

**v1.0.0** (August 20, 2026)
- Initial production release
- Complete optimization pipeline
- AI-powered features
- Natural language queries
- Local and server deployment support

---

**For technical documentation, see**: `ARCHITECTURE.md`, `DATA_SCHEMA.md`, `API_REFERENCE.md`

**For deployment instructions, see**: `DEPLOYMENT.md`

