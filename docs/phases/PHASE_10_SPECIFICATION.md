# Phase 10: AI Integration - Complete Specification

**Phase**: 10 of 12  
**Status**: In Progress  
**Estimated Effort**: 2-3 days  
**Priority**: High

---

## Overview

Phase 10 adds AI-powered natural language capabilities to PlanGram, enabling:
1. **Natural Language Queries**: Users can ask questions in plain language
2. **Recommendation Explanations**: AI explains why specific locations are recommended
3. **Insight Generation**: Automatic identification of key findings and patterns
4. **Provider Abstraction**: Support multiple AI providers (Gemini, OpenAI, etc.)

---

## Goals

### Primary
- ✅ Natural language query parsing
- ✅ Recommendation explanations (why this location?)
- ✅ Insight generation from analysis results
- ✅ Provider-agnostic architecture

### Secondary
- ⚠️ Multi-turn conversations (future)
- ⚠️ Query refinement suggestions (future)
- ⚠️ Comparative analysis explanations (future)

---

## Architecture

### AI Service Layer

```
backend/app/services/ai/
├── __init__.py
├── provider_base.py       # Abstract base class
├── provider_gemini.py     # Google Gemini implementation
├── provider_openai.py     # OpenAI implementation (optional)
├── intent_parser.py       # Parse natural language to structured queries
├── explainer.py           # Generate explanations for recommendations
└── insights.py            # Generate insights from analysis results
```

### API Layer

```
backend/app/api/
└── ai.py                  # AI endpoints
    ├── POST /api/ai/query              # Natural language query
    ├── POST /api/ai/explain            # Explain a recommendation
    └── POST /api/ai/insights           # Generate insights
```

---

## Use Cases

### Use Case 1: Natural Language Query

**User Input**: "Find the best location for a water facility in village_01 with budget under 200000"

**System Process**:
1. Parse intent → `{action: "optimize", village: "village_01", infrastructure: "water", budget: 200000}`
2. Execute optimization using existing APIs
3. Return results with AI-generated explanation

**Response**:
```json
{
  "query": "Find the best location for a water facility...",
  "intent": {
    "action": "optimize",
    "village_id": "village_01",
    "infrastructure_type": "water",
    "budget": 200000
  },
  "results": {
    "selected_locations": [...],
    "coverage_improvement": 35.5,
    "cost": 180000,
    "buildings_served": 92
  },
  "explanation": "I recommend placing a water facility at coordinates [77.688, 12.699] because:\n\n1. **Coverage Impact** (+35.5%): This location serves 92 buildings that currently lack water access within 500m.\n\n2. **Constraint Compliance** (Score: 97.5/100): The site is on public land, outside flood zones, with good road access.\n\n3. **Cost Efficiency** (₹1,957 per building): Within your ₹200,000 budget with ₹20,000 remaining for contingencies.\n\n4. **Equity**: Prioritizes the eastern cluster where coverage is only 42%, well below the village average of 59%."
}
```

### Use Case 2: Explain Recommendation

**User Input**: Click "Explain" button on a recommended location

**System Process**:
1. Receive location data + context (coverage, constraints, costs)
2. Generate human-readable explanation
3. Return structured explanation with key factors

**Response**:
```json
{
  "location": {
    "lat": 12.699,
    "lng": 77.688,
    "score": 97.5
  },
  "explanation": {
    "summary": "This location scores 97.5/100 due to high coverage impact, excellent constraint compliance, and cost efficiency.",
    "factors": [
      {
        "name": "Coverage Impact",
        "score": 98,
        "weight": 0.6,
        "description": "Serves 92 underserved buildings, improving coverage by 35.5%"
      },
      {
        "name": "Constraint Compliance",
        "score": 97,
        "weight": 0.4,
        "description": "Public land, 50m from road, no water body conflicts"
      }
    ],
    "warnings": [],
    "alternatives": "Two alternative locations score 95+ within 200m"
  }
}
```

### Use Case 3: Generate Insights

**User Input**: Complete coverage analysis for village

**System Process**:
1. Analyze coverage results
2. Identify patterns (clusters, gaps, priorities)
3. Generate actionable insights

**Response**:
```json
{
  "insights": [
    {
      "type": "critical",
      "title": "Eastern Cluster Severely Underserved",
      "description": "78 buildings in the eastern area have <30% coverage, requiring immediate attention.",
      "action": "Prioritize facility placement in this cluster",
      "impact": "Could improve coverage by 30%"
    },
    {
      "type": "opportunity",
      "title": "Efficient Central Location Available",
      "description": "A single facility at [77.688, 12.699] could serve 3 underserved clusters simultaneously.",
      "action": "Consider this location for maximum impact",
      "impact": "92 buildings served with one facility"
    },
    {
      "type": "warning",
      "title": "Diminishing Returns Above ₹400k",
      "description": "Budget analysis shows marginal coverage gains beyond 2 facilities.",
      "action": "Focus on 1-2 strategic facilities",
      "impact": "Optimize cost efficiency"
    }
  ]
}
```

---

## AI Provider Abstraction

### Base Provider Interface

```python
# backend/app/services/ai/provider_base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def parse_intent(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse natural language query into structured intent"""
        pass
    
    @abstractmethod
    async def explain_recommendation(
        self, 
        location: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Generate explanation for a recommendation"""
        pass
    
    @abstractmethod
    async def generate_insights(
        self, 
        analysis_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate insights from analysis results"""
        pass
```

### Gemini Implementation

```python
# backend/app/services/ai/provider_gemini.py

import google.generativeai as genai
from .provider_base import AIProvider

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def parse_intent(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Parse this infrastructure planning query into structured parameters:

Query: "{query}"

Available villages: {context.get('villages', [])}
Available actions: optimize, analyze, validate, generate_candidates

Return JSON with: action, village_id, infrastructure_type, budget, threshold, method

Example: {{"action": "optimize", "village_id": "village_01", "infrastructure_type": "water", "budget": 200000}}
"""
        response = self.model.generate_content(prompt)
        # Parse JSON from response
        return parse_json_response(response.text)
    
    async def explain_recommendation(
        self, 
        location: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        prompt = f"""Explain why this infrastructure location is recommended:

Location: [{location['lat']}, {location['lng']}]
Score: {location['score']}/100

Coverage Impact:
- Buildings served: {context['buildings_served']}
- Coverage improvement: +{context['coverage_improvement']}%
- Current coverage: {context['current_coverage']}%

Constraints:
- Boundary: {context['constraints']['boundary']}
- Land type: {context['constraints']['land_type']}
- Water proximity: {context['constraints']['water_distance']}m
- Road distance: {context['constraints']['road_distance']}m

Cost:
- Facility cost: ₹{context['cost']}
- Cost per building: ₹{context['cost_per_building']}

Provide a clear, structured explanation with:
1. Summary (1-2 sentences)
2. Key factors (coverage, constraints, cost)
3. Warnings or considerations
4. Comparison with alternatives
"""
        response = self.model.generate_content(prompt)
        return response.text
    
    async def generate_insights(
        self, 
        analysis_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        prompt = f"""Analyze this village infrastructure coverage data and generate 3-5 actionable insights:

Coverage: {analysis_results['coverage_percent']}%
Buildings: {analysis_results['total_buildings']} total, {analysis_results['served_buildings']} served
Underserved clusters: {len(analysis_results['clusters'])}
Priority areas: {analysis_results['high_priority_count']} high, {analysis_results['medium_priority_count']} medium

Cluster details:
{format_clusters(analysis_results['clusters'])}

Generate insights with:
- type: "critical", "opportunity", "warning"
- title: Short headline
- description: 1-2 sentences
- action: Recommended next step
- impact: Expected benefit

Return as JSON array.
"""
        response = self.model.generate_content(prompt)
        return parse_json_response(response.text)
```

### Configuration

```python
# .env additions

# AI Provider Configuration
AI_PROVIDER=gemini  # Options: gemini, openai, none
GEMINI_API_KEY=your_api_key_here
OPENAI_API_KEY=optional_key_here

# AI Settings
AI_MODEL=gemini-1.5-flash
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=2048
```

---

## API Endpoints

### 1. Natural Language Query

```
POST /api/ai/query
```

**Request**:
```json
{
  "query": "Find the best location for a water facility in village_01 with budget under 200000",
  "context": {
    "threshold": 500,
    "method": "hybrid"
  }
}
```

**Response**:
```json
{
  "query": "Find the best location...",
  "intent": {
    "action": "optimize",
    "village_id": "village_01",
    "infrastructure_type": "water",
    "budget": 200000,
    "threshold": 500,
    "method": "hybrid"
  },
  "results": {
    "selected_locations": [...],
    "coverage_improvement": 35.5,
    "cost": 180000,
    "buildings_served": 92
  },
  "explanation": "I recommend placing a water facility at..."
}
```

### 2. Explain Recommendation

```
POST /api/ai/explain
```

**Request**:
```json
{
  "location": {
    "lat": 12.699,
    "lng": 77.688,
    "score": 97.5
  },
  "context": {
    "village_id": "village_01",
    "buildings_served": 92,
    "coverage_improvement": 35.5,
    "current_coverage": 59.3,
    "cost": 180000,
    "constraints": {
      "boundary": "valid",
      "land_type": "public",
      "water_distance": 45,
      "road_distance": 50
    }
  }
}
```

**Response**:
```json
{
  "explanation": {
    "summary": "This location scores 97.5/100 due to high coverage impact...",
    "factors": [
      {
        "name": "Coverage Impact",
        "score": 98,
        "weight": 0.6,
        "description": "Serves 92 underserved buildings..."
      }
    ],
    "warnings": [],
    "alternatives": "Two alternative locations score 95+ within 200m"
  }
}
```

### 3. Generate Insights

```
POST /api/ai/insights
```

**Request**:
```json
{
  "village_id": "village_01",
  "analysis_results": {
    "coverage_percent": 59.3,
    "total_buildings": 259,
    "served_buildings": 154,
    "clusters": [...]
  }
}
```

**Response**:
```json
{
  "insights": [
    {
      "type": "critical",
      "title": "Eastern Cluster Severely Underserved",
      "description": "78 buildings in the eastern area have <30% coverage...",
      "action": "Prioritize facility placement in this cluster",
      "impact": "Could improve coverage by 30%"
    }
  ]
}
```

---

## Intent Parsing Logic

### Supported Query Patterns

| Pattern | Intent | Parameters |
|---------|--------|------------|
| "find best location for [type]" | optimize | infrastructure_type |
| "optimize [type] for village [id]" | optimize | village_id, infrastructure_type |
| "analyze coverage in [village]" | analyze | village_id |
| "generate candidates for [type]" | generate_candidates | infrastructure_type |
| "validate location [lat, lng]" | validate | lat, lng |
| "compare scenarios for [village]" | compare_scenarios | village_id |

### Parameter Extraction

```python
# Regex patterns for extraction
VILLAGE_PATTERN = r'village[_\s]?(\d+|[a-z_]+)'
BUDGET_PATTERN = r'(?:budget|cost|funds?).*?(\d+(?:,?\d+)*)'
THRESHOLD_PATTERN = r'(?:threshold|distance|radius).*?(\d+)'
INFRA_PATTERN = r'(water|waste|health|education)'
```

---

## Explanation Templates

### Structure

```python
EXPLANATION_TEMPLATE = """
{summary}

Key Factors:
1. **Coverage Impact** ({coverage_score}/100): {coverage_description}
2. **Constraint Compliance** ({constraint_score}/100): {constraint_description}
3. **Cost Efficiency**: {cost_description}
4. **Equity**: {equity_description}

{warnings}

{alternatives}
"""
```

### Scoring Interpretation

| Score | Interpretation |
|-------|---------------|
| 95-100 | Excellent - Highly recommended |
| 85-94 | Very Good - Strong candidate |
| 70-84 | Good - Suitable option |
| 50-69 | Fair - Consider alternatives |
| <50 | Poor - Not recommended |

---

## Insight Categories

### Critical Insights
- Severely underserved areas (<30% coverage)
- Major constraint violations
- Budget shortfalls
- Urgent priorities

### Opportunity Insights
- High-impact locations
- Cost-efficient options
- Multi-cluster solutions
- Quick wins

### Warning Insights
- Diminishing returns
- Over-investment
- Constraint risks
- Equity concerns

---

## Frontend Integration

### New Frontend Components

```typescript
// frontend/src/components/ai/NaturalLanguageQuery.tsx
// Natural language search bar with suggestions

// frontend/src/components/ai/ExplanationPanel.tsx
// Display AI explanations for recommendations

// frontend/src/components/ai/InsightsPanel.tsx
// Show generated insights and priorities

// frontend/src/types/ai.ts
// TypeScript types for AI responses
```

### API Client Updates

```typescript
// frontend/src/services/api.ts

export const aiAPI = {
  query: async (query: string, context?: any) => {
    const response = await axios.post('/api/ai/query', { query, context });
    return response.data;
  },
  
  explain: async (location: any, context: any) => {
    const response = await axios.post('/api/ai/explain', { location, context });
    return response.data;
  },
  
  generateInsights: async (villageId: string, analysisResults: any) => {
    const response = await axios.post('/api/ai/insights', {
      village_id: villageId,
      analysis_results: analysisResults
    });
    return response.data;
  }
};
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_ai_intent_parser.py
def test_parse_optimize_query():
    query = "Find best location for water facility in village_01 with budget 200000"
    intent = parse_intent(query)
    assert intent['action'] == 'optimize'
    assert intent['village_id'] == 'village_01'
    assert intent['infrastructure_type'] == 'water'
    assert intent['budget'] == 200000

# tests/test_ai_explainer.py
def test_explain_high_score_location():
    location = {'lat': 12.699, 'lng': 77.688, 'score': 97.5}
    context = {...}
    explanation = explain_recommendation(location, context)
    assert 'coverage' in explanation.lower()
    assert 'constraint' in explanation.lower()
    assert len(explanation) > 200  # Meaningful explanation
```

### Integration Tests

```python
# tests/test_ai_integration.py
def test_query_to_optimization():
    # Natural language query → Optimization → Explanation
    query = "optimize water for village_01 budget 300000"
    response = client.post('/api/ai/query', json={'query': query})
    assert response.status_code == 200
    assert 'intent' in response.json()
    assert 'results' in response.json()
    assert 'explanation' in response.json()
```

### Manual Test Cases

1. **Query Variations**: Test different phrasings for same intent
2. **Edge Cases**: Malformed queries, missing parameters
3. **Provider Switching**: Test Gemini vs OpenAI (if both available)
4. **Explanation Quality**: Manual review of clarity and accuracy
5. **Insight Relevance**: Verify insights match analysis results

---

## Implementation Plan

### Phase 10.1: Provider Infrastructure (Day 1)
- [ ] Create `backend/app/services/ai/` directory
- [ ] Implement `provider_base.py` (abstract interface)
- [ ] Implement `provider_gemini.py`
- [ ] Add configuration (API keys, model selection)
- [ ] Unit tests for provider

### Phase 10.2: Intent Parsing (Day 1-2)
- [ ] Implement `intent_parser.py`
- [ ] Define query patterns and regex
- [ ] Parameter extraction logic
- [ ] Fallback for unparseable queries
- [ ] Unit tests for parsing

### Phase 10.3: Explanation Generation (Day 2)
- [ ] Implement `explainer.py`
- [ ] Create explanation templates
- [ ] Scoring interpretation logic
- [ ] Warning detection
- [ ] Unit tests for explanations

### Phase 10.4: Insight Generation (Day 2)
- [ ] Implement `insights.py`
- [ ] Pattern detection (clusters, gaps, priorities)
- [ ] Insight categorization (critical, opportunity, warning)
- [ ] Actionable recommendations
- [ ] Unit tests for insights

### Phase 10.5: API Endpoints (Day 2-3)
- [ ] Create `backend/app/api/ai.py`
- [ ] POST /api/ai/query
- [ ] POST /api/ai/explain
- [ ] POST /api/ai/insights
- [ ] Register router in main.py
- [ ] Integration tests

### Phase 10.6: Frontend Integration (Day 3)
- [ ] TypeScript types (`frontend/src/types/ai.ts`)
- [ ] API client updates (`frontend/src/services/api.ts`)
- [ ] (Optional) Basic UI components for testing
- [ ] End-to-end test

### Phase 10.7: Testing & Documentation (Day 3)
- [ ] Comprehensive test suite
- [ ] Performance testing (response times)
- [ ] Documentation updates
- [ ] Example queries and responses

---

## Success Criteria

| Criterion | Target | Validation |
|-----------|--------|------------|
| Query Parsing Accuracy | >80% | Manual test of 50 queries |
| Response Time | <5s | Automated tests |
| Explanation Clarity | >4/5 rating | User testing |
| Insight Relevance | >3/5 insights actionable | Manual review |
| Provider Switching | Seamless | Test both Gemini & OpenAI |
| API Reliability | >95% success rate | Integration tests |

---

## Known Limitations

### By Design
1. **Single Turn**: No conversation history (Phase 11 feature)
2. **English Only**: No multi-language support
3. **Structured Queries**: Works best with clear, specific queries
4. **Context Limited**: Uses only provided village/analysis data

### Technical
1. **API Costs**: Gemini/OpenAI calls cost money
2. **Rate Limits**: Subject to provider rate limits
3. **Latency**: AI calls add 2-5s to response time
4. **Accuracy**: Intent parsing may fail on ambiguous queries

---

## Security Considerations

1. **API Key Management**: Store in environment variables, never commit
2. **Input Sanitization**: Validate all user queries before processing
3. **Rate Limiting**: Prevent abuse of AI endpoints (max 10/min per user)
4. **Cost Controls**: Set budget limits for AI provider spending
5. **PII Protection**: Never send sensitive data to AI providers

---

## Future Enhancements (Phase 11+)

1. **Multi-turn Conversations**: Maintain context across queries
2. **Query Refinement**: Suggest clarifications for ambiguous queries
3. **Comparative Explanations**: Explain differences between scenarios
4. **Learning**: Improve intent parsing based on user corrections
5. **Multilingual**: Support Kannada, Hindi for local users

---

## Cost Analysis

### Gemini API Pricing (estimated)
- gemini-1.5-flash: $0.075 per 1M input tokens, $0.30 per 1M output tokens
- Average query: ~500 input tokens, ~200 output tokens
- Cost per query: ~$0.00010 (very low)
- 1000 queries: ~$0.10

### Budget Recommendation
- Development: $10/month (generous for testing)
- Production: $50-100/month (depends on usage)

---

## Phase 10 Deliverables

### Code Files (8 new)
1. `backend/app/services/ai/__init__.py`
2. `backend/app/services/ai/provider_base.py`
3. `backend/app/services/ai/provider_gemini.py`
4. `backend/app/services/ai/intent_parser.py`
5. `backend/app/services/ai/explainer.py`
6. `backend/app/services/ai/insights.py`
7. `backend/app/api/ai.py`
8. `frontend/src/types/ai.ts`

### Test Files (3 new)
1. `scripts/test_phase10_unit.py`
2. `scripts/test_phase10_integration.py`
3. `scripts/test_phase10_e2e.py`

### Documentation (3 new)
1. `PHASE_10_SPECIFICATION.md` (this file)
2. `PHASE_10_COMPLETE.md` (after testing)
3. `docs/AI_INTEGRATION.md` (user guide)

---

## Timeline

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| 1 | Provider infrastructure + Intent parsing | Base classes, Gemini provider, parser |
| 2 | Explanations + Insights + API endpoints | Explainer, insights, 3 API endpoints |
| 3 | Frontend integration + Testing + Docs | TypeScript types, tests, documentation |

**Total**: 3 days

---

**Phase 10 Status**: ✅ **SPECIFICATION COMPLETE**  
**Ready to Implement**: ✅ **YES**  
**Next Step**: Create provider infrastructure

---

*PlanGram - Explore. Simulate. Plan.*  
*Phase 10: AI-Powered Decision Support*
