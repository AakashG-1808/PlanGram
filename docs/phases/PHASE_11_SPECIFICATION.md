# Phase 11: Machine Learning - Complete Specification

**Phase**: 11 of 12  
**Status**: Specification Phase  
**Estimated Effort**: 4-5 days  
**Priority**: Optional (Low)

---

## Overview

Phase 11 adds machine learning capabilities to PlanGram to learn from historical infrastructure placements and predict success, recommend optimal locations, and detect anomalies. This phase is **optional** as the system is fully functional without it.

---

## ⚠️ Important Considerations

### Why This Phase is Optional

1. **No Historical Data**: Currently only 2 synthetic villages exist (no real historical placement data)
2. **Working System**: Optimization already provides excellent recommendations (97-99/100 scores)
3. **Data Requirements**: ML requires 50-100+ historical placements for meaningful training
4. **Complexity**: Adds significant complexity for marginal improvement
5. **MVP Status**: Phase 12 (Polish) is more critical for production deployment

### When to Implement Phase 11

- ✅ **After deployment** with 50+ real villages
- ✅ **After 6-12 months** of usage with real placement data
- ✅ **After Phase 12** is complete (production-ready)
- ✅ **When pattern analysis** shows unexpected failures/successes

### Recommendation

**Skip Phase 11 and proceed to Phase 12 (Demo + Polish)** for faster MVP completion.

If you still want to proceed with Phase 11, here's the complete specification:

---

## Goals

### Primary
- ✅ Feature engineering from placement data
- ✅ Success prediction model (will this placement work well?)
- ✅ Location recommendations (ML-enhanced candidate generation)
- ✅ Anomaly detection (identify unusual patterns)

### Secondary
- ⚠️ Pattern discovery (what makes placements successful?)
- ⚠️ Risk assessment (probability of issues)
- ⚠️ Optimization enhancement (ML-guided optimization)

---

## Architecture

### ML Service Layer

```
backend/app/services/ml/
├── __init__.py
├── feature_engineering.py    # Extract features from placements
├── success_predictor.py       # Predict placement success
├── location_recommender.py    # ML-based location recommendations
├── anomaly_detector.py        # Detect unusual patterns
├── model_trainer.py           # Train and update models
└── models/                    # Saved ML models
    ├── success_model.pkl
    ├── location_model.pkl
    └── anomaly_model.pkl
```

### API Layer

```
backend/app/api/
└── ml.py                      # ML endpoints
    ├── POST /api/ml/predict-success      # Predict placement success
    ├── POST /api/ml/recommend-locations  # ML-enhanced recommendations
    ├── POST /api/ml/detect-anomalies     # Detect anomalies
    ├── POST /api/ml/train                # Retrain models (admin)
    └── GET  /api/ml/model-stats          # Model performance metrics
```

---

## Feature Engineering

### Features to Extract

#### Spatial Features (15)
1. **Coverage metrics**: Current coverage %, gap size, cluster density
2. **Distance metrics**: Avg distance to buildings, nearest facility distance
3. **Terrain features**: Elevation variance, slope, terrain complexity
4. **Accessibility**: Road density, road distance, connectivity score
5. **Land use**: Public land %, water body proximity, parcel fragmentation

#### Demographic Features (8)
6. **Population**: Total, density, household size
7. **Distribution**: Population spread, clustering coefficient
8. **Priority**: High/medium/low priority area count

#### Constraint Features (10)
9. **Violations**: Boundary, parcel, water proximity violations
10. **Suitability**: Overall suitability score, constraint severity
11. **Risk factors**: Water risk, accessibility risk

#### Historical Features (12)
12. **Past placements**: Number, success rate, avg score
13. **Temporal**: Season placed, time since last placement
14. **Maintenance**: Issues reported, usage patterns

**Total Features**: ~45 features

### Feature Importance

Expected top 10 features:
1. Current coverage %
2. Buildings in 500m radius
3. Distance to nearest facility
4. Suitability score
5. Road accessibility
6. Population density
7. Land type (public/private)
8. Water body distance
9. Cluster size
10. Budget per capita

---

## Success Prediction Model

### Definition of Success

A placement is "successful" if:
- ✅ Actual coverage improvement ≥ 80% of predicted
- ✅ No major constraint violations occurred
- ✅ Usage is ≥ 70% of capacity after 6 months
- ✅ No major maintenance issues in first year
- ✅ Community satisfaction ≥ 3.5/5

**Binary Classification**: Success (1) or Failure (0)

### Model Architecture

**Approach**: Gradient Boosting (XGBoost)

**Why**:
- Works well with tabular data
- Handles non-linear relationships
- Feature importance built-in
- Fast inference (<10ms)

**Alternative**: Random Forest (simpler, similar performance)

### Training Process

```python
# Pseudo-code
def train_success_model(historical_placements):
    # 1. Feature extraction
    X = extract_features(historical_placements)
    y = get_success_labels(historical_placements)
    
    # 2. Train/test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    
    # 3. Train XGBoost
    model = XGBClassifier(
        max_depth=5,
        n_estimators=100,
        learning_rate=0.1
    )
    model.fit(X_train, y_train)
    
    # 4. Evaluate
    accuracy = model.score(X_test, y_test)
    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    
    # 5. Save model
    save_model(model, 'success_model.pkl')
    
    return model, accuracy, auc
```

### Expected Performance

With 50+ placements:
- Accuracy: 75-85%
- AUC: 0.80-0.90
- Precision: 0.70-0.80
- Recall: 0.75-0.85

---

## Location Recommender

### ML-Enhanced Candidate Generation

**How it works**:
1. Generate 100 candidates using existing methods (hybrid)
2. Extract features for each candidate
3. Predict success probability for each
4. Rank by: `score = 0.5 * coverage_score + 0.3 * suitability + 0.2 * success_probability`
5. Return top N with confidence scores

### Model Architecture

**Approach**: Regression (predict score 0-100)

**Model**: LightGBM (faster than XGBoost)

### Comparison with Rule-Based

| Method | Coverage Score | Suitability | Success Rate |
|--------|---------------|-------------|--------------|
| Rule-based (Phase 6) | 99.2/100 | 97.5/100 | Unknown |
| ML-enhanced | 98.5/100 | 98.2/100 | 85% predicted |

**Benefit**: ML adds success prediction, rule-based is already excellent for scoring.

---

## Anomaly Detection

### What to Detect

1. **Unusual Patterns**: Placements that deviate from typical patterns
2. **High-Risk Locations**: Low predicted success despite good scores
3. **Data Quality Issues**: Inconsistent or suspicious data
4. **Unexpected Failures**: Locations that should work but didn't

### Model Architecture

**Approach**: Isolation Forest (unsupervised)

**Why**:
- No labels needed
- Detects outliers effectively
- Fast inference

### Anomaly Types

| Type | Description | Action |
|------|-------------|--------|
| **Type 1**: High score, low success | Flag for review | Manual validation |
| **Type 2**: Low score, high success | Pattern discovery | Update scoring rules |
| **Type 3**: Unusual features | Data quality | Verify inputs |
| **Type 4**: Unexpected failure | Investigation | Root cause analysis |

---

## API Endpoints

### 1. Predict Success

```
POST /api/ml/predict-success
```

**Request**:
```json
{
  "village_id": "village_01",
  "location": [77.688, 12.699],
  "infrastructure_type": "water",
  "features": {
    "current_coverage": 59.3,
    "buildings_nearby": 92,
    "suitability": 97.5
  }
}
```

**Response**:
```json
{
  "success_probability": 0.85,
  "confidence": "high",
  "risk_factors": [
    "Water body proximity moderate (45m)"
  ],
  "recommendations": [
    "Add drainage system for water management"
  ]
}
```

### 2. ML-Enhanced Recommendations

```
POST /api/ml/recommend-locations
```

**Request**:
```json
{
  "village_id": "village_01",
  "infrastructure_type": "water",
  "num_recommendations": 10
}
```

**Response**:
```json
{
  "recommendations": [
    {
      "location": [77.688, 12.699],
      "coverage_score": 98.5,
      "suitability_score": 98.2,
      "success_probability": 0.87,
      "confidence": "high",
      "rank": 1
    }
  ],
  "model_version": "1.0",
  "trained_on": "2024-08-15"
}
```

### 3. Detect Anomalies

```
POST /api/ml/detect-anomalies
```

**Request**:
```json
{
  "village_id": "village_01",
  "placements": [...]
}
```

**Response**:
```json
{
  "anomalies": [
    {
      "placement_id": "p123",
      "anomaly_score": 0.92,
      "type": "high_risk",
      "description": "High score but low predicted success",
      "recommendation": "Manual review recommended"
    }
  ]
}
```

### 4. Train Models (Admin)

```
POST /api/ml/train
```

**Request**:
```json
{
  "model_type": "success_predictor",
  "data_source": "historical_placements",
  "test_size": 0.2
}
```

**Response**:
```json
{
  "status": "success",
  "metrics": {
    "accuracy": 0.82,
    "auc": 0.88,
    "precision": 0.79,
    "recall": 0.81
  },
  "training_samples": 127,
  "model_version": "1.1"
}
```

### 5. Model Statistics

```
GET /api/ml/model-stats
```

**Response**:
```json
{
  "models": {
    "success_predictor": {
      "version": "1.1",
      "accuracy": 0.82,
      "trained_on": "2024-08-15",
      "training_samples": 127,
      "status": "active"
    },
    "location_recommender": {
      "version": "1.0",
      "mae": 2.3,
      "trained_on": "2024-08-10",
      "training_samples": 85,
      "status": "active"
    },
    "anomaly_detector": {
      "version": "1.0",
      "contamination": 0.05,
      "trained_on": "2024-08-01",
      "training_samples": 200,
      "status": "active"
    }
  }
}
```

---

## Data Requirements

### Minimum Data for Training

| Model | Minimum Samples | Recommended |
|-------|----------------|-------------|
| Success Predictor | 50 placements | 100-200 |
| Location Recommender | 30 placements | 80-150 |
| Anomaly Detector | 100 data points | 200-500 |

### Data Collection Strategy

**Phase 1**: Simulate historical data (for development/testing)
- Generate 100 synthetic placement records
- Add success labels (rule-based simulation)
- Use for model development

**Phase 2**: Collect real data (post-deployment)
- Track actual placements
- Collect usage metrics
- Survey community satisfaction
- Monitor maintenance issues

**Phase 3**: Continuous learning
- Retrain models quarterly
- Update based on new placements
- A/B test ML vs rule-based

---

## Implementation Plan

### Phase 11.1: Feature Engineering (Day 1-2)
- [ ] Implement feature extraction from placements
- [ ] Create feature engineering pipeline
- [ ] Generate synthetic historical data
- [ ] Validate feature quality
- [ ] Unit tests

### Phase 11.2: Success Prediction (Day 2-3)
- [ ] Implement XGBoost success predictor
- [ ] Train on synthetic data
- [ ] Evaluate model performance
- [ ] API endpoint for predictions
- [ ] Integration tests

### Phase 11.3: Location Recommender (Day 3-4)
- [ ] Implement LightGBM recommender
- [ ] Integrate with candidate generation
- [ ] Compare with rule-based approach
- [ ] API endpoint for recommendations
- [ ] Performance tests

### Phase 11.4: Anomaly Detection (Day 4)
- [ ] Implement Isolation Forest detector
- [ ] Define anomaly types
- [ ] API endpoint for detection
- [ ] Visualization of anomalies
- [ ] Unit tests

### Phase 11.5: Model Management (Day 5)
- [ ] Model training pipeline
- [ ] Model versioning
- [ ] Performance monitoring
- [ ] Retraining automation
- [ ] Documentation

---

## Technology Stack

### ML Libraries

```python
# requirements.txt additions
scikit-learn==1.3.2         # Core ML algorithms
xgboost==2.0.3             # Gradient boosting
lightgbm==4.1.0            # Fast gradient boosting
numpy==1.26.3              # Already included
pandas==2.2.0              # Already included
joblib==1.3.2              # Model serialization
```

### Model Storage

- **Format**: Pickle (.pkl) or Joblib
- **Location**: `backend/app/services/ml/models/`
- **Versioning**: Filename includes version (e.g., `success_model_v1.1.pkl`)

---

## Testing Strategy

### Unit Tests
- Feature extraction correctness
- Model training pipeline
- Prediction accuracy on test data
- Anomaly detection on known outliers

### Integration Tests
- API endpoints functional
- Model loading/saving works
- Feature pipeline end-to-end
- Performance within limits (<100ms inference)

### Model Tests
- Accuracy ≥ 75% on test set
- AUC ≥ 0.80 for success predictor
- MAE ≤ 5.0 for location recommender
- Anomaly detection rate 5-10%

---

## Performance Requirements

| Operation | Target | Status |
|-----------|--------|--------|
| Feature extraction | <50ms | - |
| Success prediction | <10ms | - |
| Location recommendation | <500ms | - |
| Anomaly detection | <100ms | - |
| Model training | <5min | - |

---

## Success Criteria

| Criterion | Target | Validation |
|-----------|--------|------------|
| Success prediction accuracy | >75% | Test set evaluation |
| ML vs rule-based comparison | Similar | Side-by-side testing |
| Anomaly detection rate | 5-10% | Manual review of flagged items |
| API response time | <100ms | Performance tests |
| Model retraining | <5min | Automated pipeline |

---

## Known Limitations

### Data Limitations
1. **Synthetic Data**: Training on simulated data initially
2. **Small Dataset**: Only 2 villages (need 50+ for real training)
3. **No Ground Truth**: No actual success/failure data yet

### Model Limitations
1. **Cold Start**: Poor predictions without historical data
2. **Overfitting Risk**: With limited data, models may overfit
3. **Feature Quality**: Synthetic features may not reflect reality

### Practical Limitations
1. **Marginal Improvement**: Rule-based already 97-99% effective
2. **Complexity**: Adds maintenance burden
3. **Interpretability**: ML models less interpretable than rules

---

## Why Skip Phase 11 (Recommendation)

### Current System Performance

Rule-based optimization (Phases 6-7):
- ✅ **Coverage scores**: 97-99/100 (excellent)
- ✅ **Suitability scores**: 95-98/100 (excellent)
- ✅ **Cost efficiency**: ₹1,957-₹5,047 per building
- ✅ **Validated**: Real-world constraints checked

### ML Would Add

- ⚠️ **Success prediction**: Useful but requires historical data
- ⚠️ **Pattern discovery**: Needs 50-100+ placements first
- ⚠️ **Marginal improvement**: Rule-based already near-optimal
- ⚠️ **Complexity**: Significant development and maintenance

### Better Approach

1. **Deploy Phase 12 first** (production-ready)
2. **Collect real data** (6-12 months)
3. **Revisit Phase 11** when you have 50+ historical placements
4. **A/B test** ML vs rule-based with real data

---

## Alternative: Lightweight ML

If you insist on some ML in Phase 11, consider a **lightweight version**:

### Lightweight Phase 11 (2 days)

**Scope**:
1. ✅ Feature extraction framework only
2. ✅ Placeholder ML service (returns rule-based results)
3. ✅ API endpoints (prepared for future ML)
4. ⏭️ Skip actual model training (wait for real data)

**Benefits**:
- Infrastructure ready for future ML
- No time wasted on synthetic data training
- API contracts defined
- Easy to add real ML later

---

## Recommendation

**⚠️ SKIP PHASE 11 - Proceed to Phase 12 (Demo + Polish)**

**Rationale**:
1. System is already excellent (97-99/100 scores)
2. No historical data for meaningful training
3. Phase 12 is critical for MVP completion
4. ML can be added post-deployment with real data

**Alternative Path**:
- Phase 12: Demo + Polish (2-3 days)
- Deploy MVP
- Collect 6-12 months of data
- Return to Phase 11 with real data
- A/B test ML improvements

---

**Phase 11 Status**: ✅ **SPECIFICATION COMPLETE**  
**Implementation Status**: ⏸️ **DEFERRED - Not Recommended**  
**Next Recommended**: 🚀 **PHASE 12 (Demo + Polish)**

---

*PlanGram - Explore. Simulate. Plan.*  
*Machine Learning: Specified but deferred until real data available*

