"""AI-powered natural language and explanation endpoints."""

import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from ..services.ai import (
    GeminiProvider,
    IntentParser,
    RecommendationExplainer,
    InsightGenerator
)

router = APIRouter(prefix="/api/ai", tags=["ai"])


# Request/Response Models

class QueryRequest(BaseModel):
    """Natural language query request."""
    query: str = Field(..., description="Natural language query", min_length=5)
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class QueryResponse(BaseModel):
    """Natural language query response."""
    query: str
    intent: Dict[str, Any]
    results: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None
    error: Optional[str] = None


class ExplainRequest(BaseModel):
    """Explanation request."""
    location: Dict[str, Any] = Field(..., description="Location data (lat, lng, score)")
    context: Dict[str, Any] = Field(..., description="Analysis context")


class ExplainResponse(BaseModel):
    """Explanation response."""
    summary: str
    full_explanation: str
    factors: list[Dict[str, Any]]
    warnings: list[str]
    alternatives: Optional[str] = None


class InsightsRequest(BaseModel):
    """Insights generation request."""
    village_id: str = Field(..., description="Village ID")
    analysis_results: Dict[str, Any] = Field(..., description="Coverage analysis results")


class InsightsResponse(BaseModel):
    """Insights generation response."""
    insights: list[Dict[str, Any]]


# Dependency: Get AI services

def get_ai_services():
    """Initialize AI services (singleton pattern)."""
    ai_enabled = os.getenv('AI_PROVIDER', 'none') != 'none'
    
    if ai_enabled and os.getenv('AI_PROVIDER') == 'gemini':
        try:
            ai_provider = GeminiProvider()
        except ValueError:
            # No API key configured
            ai_provider = None
    else:
        ai_provider = None
    
    intent_parser = IntentParser(ai_provider=ai_provider)
    explainer = RecommendationExplainer(ai_provider=ai_provider)
    insight_generator = InsightGenerator(ai_provider=ai_provider)
    
    return {
        'intent_parser': intent_parser,
        'explainer': explainer,
        'insight_generator': insight_generator
    }


# Endpoints

@router.post("/query", response_model=QueryResponse)
async def natural_language_query(
    request: QueryRequest,
    services: Dict = Depends(get_ai_services)
):
    """
    Parse natural language query and execute corresponding action.
    
    Example queries:
    - "Find best water facility location in village_01 with budget 200000"
    - "Analyze coverage in village_02"
    - "Generate 20 candidates for water using hybrid method"
    """
    try:
        intent_parser = services['intent_parser']
        
        # Parse query
        intent = await intent_parser.parse(request.query, request.context or {})
        
        # Validate intent
        intent = intent_parser.validate_intent(intent)
        
        if intent.get('action') == 'error':
            return QueryResponse(
                query=request.query,
                intent=intent,
                error=intent.get('error', 'Unknown error')
            )
        
        # Return parsed intent
        # Note: Actual execution would be done by frontend calling appropriate APIs
        return QueryResponse(
            query=request.query,
            intent=intent,
            results=None,
            explanation=None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.post("/explain", response_model=ExplainResponse)
async def explain_recommendation(
    request: ExplainRequest,
    services: Dict = Depends(get_ai_services)
):
    """
    Generate explanation for why a location is recommended.
    
    The explanation includes:
    - Summary of recommendation
    - Key scoring factors (coverage, constraints, cost)
    - Warnings or concerns
    - Information about alternative locations
    """
    try:
        explainer = services['explainer']
        
        # Generate explanation
        explanation = await explainer.explain(request.location, request.context)
        
        return ExplainResponse(**explanation)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation generation failed: {str(e)}")


@router.post("/insights", response_model=InsightsResponse)
async def generate_insights(
    request: InsightsRequest,
    services: Dict = Depends(get_ai_services)
):
    """
    Generate actionable insights from coverage analysis.
    
    Insights include:
    - Critical issues requiring immediate attention
    - Opportunities for high-impact improvements
    - Warnings about challenges or limitations
    
    Each insight includes:
    - type: "critical", "opportunity", or "warning"
    - title: Short headline
    - description: Detailed explanation
    - action: Recommended next step
    - impact: Expected benefit
    """
    try:
        insight_generator = services['insight_generator']
        
        # Generate insights
        insights = await insight_generator.generate(request.analysis_results)
        
        return InsightsResponse(insights=insights)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insight generation failed: {str(e)}")


@router.get("/health")
async def ai_health_check():
    """
    Check AI service health and configuration.
    
    Returns:
    - AI provider status (enabled/disabled)
    - Provider type (gemini, openai, none)
    - API key configured status
    """
    ai_provider = os.getenv('AI_PROVIDER', 'none')
    ai_enabled = ai_provider != 'none'
    
    api_key_configured = False
    if ai_provider == 'gemini':
        api_key_configured = bool(os.getenv('GEMINI_API_KEY'))
    elif ai_provider == 'openai':
        api_key_configured = bool(os.getenv('OPENAI_API_KEY'))
    
    return {
        'ai_enabled': ai_enabled,
        'provider': ai_provider,
        'api_key_configured': api_key_configured,
        'fallback_mode': not (ai_enabled and api_key_configured),
        'features': {
            'intent_parsing': True,  # Always available (regex fallback)
            'ai_explanations': ai_enabled and api_key_configured,
            'ai_insights': ai_enabled and api_key_configured
        }
    }
