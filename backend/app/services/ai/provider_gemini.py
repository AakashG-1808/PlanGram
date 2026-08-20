"""Google Gemini AI provider implementation."""

import json
import re
import os
from typing import Dict, Any, List, Optional

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from .provider_base import AIProvider


class GeminiProvider(AIProvider):
    """Google Gemini implementation of AI provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            model: Model to use (default: gemini-1.5-flash)
        """
        if not GENAI_AVAILABLE:
            raise ImportError(
                "google-generativeai package not installed. "
                "Install with: pip install google-generativeai"
            )
        
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not provided and not found in environment")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
        self.temperature = float(os.getenv('AI_TEMPERATURE', '0.7'))
    
    async def parse_intent(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse natural language query into structured intent."""
        
        villages = context.get('villages', ['village_01', 'village_02'])
        
        prompt = f"""Parse this infrastructure planning query into structured JSON parameters.

Query: "{query}"

Available Context:
- Villages: {villages}
- Infrastructure types: water, waste, health, education
- Actions: optimize, analyze, validate, generate_candidates, compare_scenarios
- Generation methods: grid, gap, hybrid

Extract these parameters if mentioned:
- action (required): optimize, analyze, validate, generate_candidates
- village_id: which village (e.g., village_01)
- infrastructure_type: water, waste, health, or education
- budget: numeric budget amount (extract digits only)
- threshold: distance threshold in meters (default 500)
- method: grid, gap, or hybrid (for candidate generation)
- num_candidates: number of candidates to generate
- lat, lng: coordinates for validation queries

Return ONLY valid JSON, no markdown formatting:
{{"action": "...", "village_id": "...", "infrastructure_type": "...", ...}}

Examples:
Query: "Find best water facility location in village_01 with budget 200000"
{{"action": "optimize", "village_id": "village_01", "infrastructure_type": "water", "budget": 200000}}

Query: "Analyze coverage in village_02"
{{"action": "analyze", "village_id": "village_02"}}

Query: "Generate 20 candidates for water using hybrid method in village_01"
{{"action": "generate_candidates", "village_id": "village_01", "infrastructure_type": "water", "method": "hybrid", "num_candidates": 20}}

Now parse this query:
"{query}"
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=512,
                )
            )
            
            # Extract JSON from response
            intent = self._extract_json(response.text)
            
            # Validate required fields
            if 'action' not in intent:
                raise ValueError("No action identified in query")
            
            # Set defaults
            intent.setdefault('threshold', 500)
            intent.setdefault('method', 'hybrid')
            
            return intent
            
        except Exception as e:
            # Fallback: return error intent
            return {
                'action': 'error',
                'error': f'Failed to parse query: {str(e)}',
                'original_query': query
            }
    
    async def explain_recommendation(
        self, 
        location: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Generate explanation for why a location is recommended."""
        
        lat = location.get('lat', location.get('latitude', 0))
        lng = location.get('lng', location.get('longitude', 0))
        score = location.get('score', 0)
        
        buildings_served = context.get('buildings_served', 0)
        coverage_improvement = context.get('coverage_improvement', 0)
        current_coverage = context.get('current_coverage', 0)
        cost = context.get('cost', 0)
        cost_per_building = context.get('cost_per_building', 0)
        
        constraints = context.get('constraints', {})
        boundary = constraints.get('boundary', 'unknown')
        land_type = constraints.get('land_type', 'unknown')
        water_distance = constraints.get('water_distance', 0)
        road_distance = constraints.get('road_distance', 0)
        
        prompt = f"""Explain why this infrastructure location is recommended for village planners.

Location Details:
- Coordinates: [{lat:.6f}, {lng:.6f}]
- Overall Score: {score:.1f}/100

Coverage Impact:
- Buildings served: {buildings_served}
- Coverage improvement: +{coverage_improvement:.1f}%
- Current village coverage: {current_coverage:.1f}%

Constraint Compliance:
- Boundary check: {boundary}
- Land type: {land_type}
- Distance to water: {water_distance}m
- Distance to road: {road_distance}m

Cost Analysis:
- Total facility cost: ₹{cost:,}
- Cost per building served: ₹{cost_per_building:,}

Generate a clear, structured explanation in this format:

**Summary** (1-2 sentences on why this location is recommended)

**Key Factors:**
1. **Coverage Impact**: Explain buildings served and coverage improvement
2. **Constraint Compliance**: Explain boundary, land, water, road factors
3. **Cost Efficiency**: Explain cost per building and budget utilization
4. **Equity Considerations**: Explain which underserved areas benefit

**Warnings** (if any): Any concerns or considerations

**Alternatives**: Mention if other locations are comparable

Write in a professional but accessible tone for government planners.
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=1024,
                )
            )
            return response.text.strip()
            
        except Exception as e:
            return f"Error generating explanation: {str(e)}"
    
    async def generate_insights(
        self, 
        analysis_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable insights from analysis results."""
        
        coverage_percent = analysis_results.get('coverage_percent', 0)
        total_buildings = analysis_results.get('total_buildings', 0)
        served_buildings = analysis_results.get('served_buildings', 0)
        unserved_buildings = total_buildings - served_buildings
        
        clusters = analysis_results.get('clusters', [])
        high_priority = analysis_results.get('high_priority_count', 0)
        medium_priority = analysis_results.get('medium_priority_count', 0)
        
        # Format cluster info
        cluster_info = []
        for i, cluster in enumerate(clusters[:5]):  # Top 5 clusters
            cluster_info.append(
                f"Cluster {i+1}: {cluster.get('building_count', 0)} buildings, "
                f"priority: {cluster.get('priority', 'unknown')}"
            )
        cluster_text = '\n'.join(cluster_info)
        
        prompt = f"""Analyze this village infrastructure coverage data and generate 3-5 actionable insights.

Current Status:
- Coverage: {coverage_percent:.1f}%
- Buildings: {total_buildings} total, {served_buildings} served, {unserved_buildings} unserved
- Underserved clusters identified: {len(clusters)}
- High priority areas: {high_priority}
- Medium priority areas: {medium_priority}

Underserved Clusters:
{cluster_text}

Generate 3-5 insights with different types:
1. Critical insight: Most urgent issue requiring immediate attention
2. Opportunity insight: High-impact, cost-effective opportunity
3. Warning insight: Risk or concern to be aware of
4-5. Additional insights as relevant

For each insight, return JSON with:
- type: "critical", "opportunity", or "warning"
- title: Short headline (5-8 words)
- description: Clear explanation (1-2 sentences)
- action: Specific recommended next step
- impact: Expected benefit or outcome

Return ONLY a JSON array, no markdown formatting:
[
  {{
    "type": "critical",
    "title": "Eastern Cluster Severely Underserved",
    "description": "78 buildings in the eastern area have less than 30% coverage, well below the village average.",
    "action": "Prioritize facility placement in the eastern cluster to address the coverage gap",
    "impact": "Could improve overall coverage by 25-30%"
  }},
  ...
]
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=2048,
                )
            )
            
            # Extract JSON array from response
            insights = self._extract_json(response.text)
            
            # Ensure it's a list
            if not isinstance(insights, list):
                insights = [insights]
            
            return insights
            
        except Exception as e:
            # Fallback: generate basic insights without AI
            return self._generate_basic_insights(analysis_results)
    
    def _extract_json(self, text: str) -> Any:
        """Extract JSON from text that may contain markdown or other formatting."""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Find JSON object or array
        json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            return json.loads(json_str)
        
        # If no JSON found, try parsing entire text
        return json.loads(text)
    
    def _generate_basic_insights(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate basic insights without AI as fallback."""
        insights = []
        
        coverage_percent = analysis_results.get('coverage_percent', 0)
        unserved_buildings = analysis_results.get('total_buildings', 0) - analysis_results.get('served_buildings', 0)
        clusters = analysis_results.get('clusters', [])
        
        # Critical: Low coverage
        if coverage_percent < 50:
            insights.append({
                'type': 'critical',
                'title': 'Low Village Coverage Detected',
                'description': f'Only {coverage_percent:.1f}% of buildings have adequate access to infrastructure.',
                'action': 'Prioritize infrastructure expansion to underserved areas',
                'impact': f'Could serve {unserved_buildings} additional buildings'
            })
        
        # Opportunity: Large clusters
        if clusters:
            largest_cluster = max(clusters, key=lambda c: c.get('building_count', 0))
            insights.append({
                'type': 'opportunity',
                'title': 'Large Underserved Cluster Identified',
                'description': f'A cluster of {largest_cluster.get("building_count", 0)} buildings lacks adequate coverage.',
                'action': 'Place facility near this cluster for maximum impact',
                'impact': 'Single facility could serve multiple clusters'
            })
        
        # Warning: Many clusters
        if len(clusters) > 5:
            insights.append({
                'type': 'warning',
                'title': 'Fragmented Coverage Pattern',
                'description': f'{len(clusters)} separate underserved clusters detected, requiring multiple facilities.',
                'action': 'Plan multi-phase implementation or increase budget',
                'impact': 'Complete coverage may require significant investment'
            })
        
        return insights
