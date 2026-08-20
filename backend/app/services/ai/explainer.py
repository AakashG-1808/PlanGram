"""Generate explanations for recommendations."""

from typing import Dict, Any, Optional


class RecommendationExplainer:
    """Generate human-readable explanations for infrastructure recommendations."""
    
    def __init__(self, ai_provider=None):
        """
        Initialize explainer.
        
        Args:
            ai_provider: Optional AI provider for enhanced explanations
        """
        self.ai_provider = ai_provider
    
    async def explain(
        self, 
        location: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate explanation for a recommended location.
        
        Args:
            location: Location data (lat, lng, score)
            context: Analysis context (coverage, constraints, costs)
            
        Returns:
            Explanation dictionary with summary, factors, warnings
        """
        # Try AI provider first if available
        if self.ai_provider:
            try:
                ai_explanation = await self.ai_provider.explain_recommendation(location, context)
                return {
                    'summary': self._extract_summary(ai_explanation),
                    'full_explanation': ai_explanation,
                    'factors': self._extract_factors(context),
                    'warnings': self._extract_warnings(context),
                    'alternatives': self._extract_alternatives(context)
                }
            except Exception:
                # Fall through to template-based explanation
                pass
        
        # Fallback to template-based explanation
        return self._generate_template_explanation(location, context)
    
    def _generate_template_explanation(
        self, 
        location: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate explanation using templates."""
        
        score = location.get('score', 0)
        lat = location.get('lat', location.get('latitude', 0))
        lng = location.get('lng', location.get('longitude', 0))
        
        # Extract context data
        buildings_served = context.get('buildings_served', 0)
        coverage_improvement = context.get('coverage_improvement', 0)
        current_coverage = context.get('current_coverage', 0)
        cost = context.get('cost', 0)
        cost_per_building = context.get('cost_per_building', 0)
        
        # Generate summary
        summary = self._generate_summary(score, buildings_served, coverage_improvement)
        
        # Generate factors
        factors = self._extract_factors(context)
        
        # Generate full explanation
        full_explanation = f"""## Summary

{summary}

## Key Factors

### 1. Coverage Impact
This location would serve {buildings_served} buildings, improving village coverage by {coverage_improvement:.1f}% (from {current_coverage:.1f}% to {current_coverage + coverage_improvement:.1f}%).

### 2. Constraint Compliance
{self._format_constraints(context.get('constraints', {}))}

### 3. Cost Efficiency
Total cost: ₹{cost:,}
Cost per building served: ₹{cost_per_building:,}

{self._format_cost_assessment(cost_per_building)}

### 4. Location Details
Coordinates: [{lat:.6f}, {lng:.6f}]
Overall Score: {score:.1f}/100

{self._format_warnings(context)}

{self._format_alternatives(context)}
"""
        
        return {
            'summary': summary,
            'full_explanation': full_explanation,
            'factors': factors,
            'warnings': self._extract_warnings(context),
            'alternatives': self._extract_alternatives(context)
        }
    
    def _generate_summary(
        self, 
        score: float, 
        buildings_served: int, 
        coverage_improvement: float
    ) -> str:
        """Generate concise summary."""
        
        rating = self._score_to_rating(score)
        
        return (
            f"This location scores {score:.1f}/100 ({rating}), serving {buildings_served} buildings "
            f"and improving coverage by {coverage_improvement:.1f}%."
        )
    
    def _extract_summary(self, ai_explanation: str) -> str:
        """Extract summary from AI explanation."""
        # Look for summary section or first paragraph
        lines = ai_explanation.split('\n')
        for i, line in enumerate(lines):
            if 'summary' in line.lower() and i + 1 < len(lines):
                return lines[i + 1].strip()
        
        # Return first non-empty line
        for line in lines:
            if line.strip() and not line.startswith('#'):
                return line.strip()
        
        return ai_explanation[:200] + '...'
    
    def _extract_factors(self, context: Dict[str, Any]) -> list[Dict[str, Any]]:
        """Extract scoring factors."""
        factors = []
        
        # Coverage factor
        coverage_improvement = context.get('coverage_improvement', 0)
        buildings_served = context.get('buildings_served', 0)
        coverage_score = min(100, (coverage_improvement / 50.0) * 100)  # 50% improvement = 100 score
        
        factors.append({
            'name': 'Coverage Impact',
            'score': coverage_score,
            'weight': 0.6,
            'description': f'Serves {buildings_served} buildings, +{coverage_improvement:.1f}% coverage'
        })
        
        # Constraint factor
        constraints = context.get('constraints', {})
        constraint_score = self._calculate_constraint_score(constraints)
        
        factors.append({
            'name': 'Constraint Compliance',
            'score': constraint_score,
            'weight': 0.4,
            'description': self._format_constraints(constraints)
        })
        
        return factors
    
    def _calculate_constraint_score(self, constraints: Dict[str, Any]) -> float:
        """Calculate constraint compliance score."""
        score = 100.0
        
        # Boundary check
        if constraints.get('boundary') != 'valid':
            score -= 50
        
        # Land type
        land_type = constraints.get('land_type', 'unknown')
        if land_type == 'private':
            score -= 30
        elif land_type == 'restricted':
            score -= 40
        
        # Water distance
        water_distance = constraints.get('water_distance', 999)
        if water_distance < 10:
            score -= 40
        elif water_distance < 30:
            score -= 10
        
        # Road distance
        road_distance = constraints.get('road_distance', 999)
        if road_distance > 200:
            score -= 20
        elif road_distance > 100:
            score -= 10
        
        return max(0, score)
    
    def _format_constraints(self, constraints: Dict[str, Any]) -> str:
        """Format constraint information."""
        parts = []
        
        boundary = constraints.get('boundary', 'unknown')
        parts.append(f"Boundary: {boundary}")
        
        land_type = constraints.get('land_type', 'unknown')
        parts.append(f"Land type: {land_type}")
        
        water_distance = constraints.get('water_distance', 0)
        if water_distance > 0:
            parts.append(f"Water distance: {water_distance}m")
        
        road_distance = constraints.get('road_distance', 0)
        if road_distance > 0:
            parts.append(f"Road distance: {road_distance}m")
        
        return ', '.join(parts)
    
    def _format_cost_assessment(self, cost_per_building: int) -> str:
        """Format cost efficiency assessment."""
        if cost_per_building < 2000:
            return "**Excellent cost efficiency** - Well below typical costs."
        elif cost_per_building < 4000:
            return "**Good cost efficiency** - Within acceptable range."
        elif cost_per_building < 6000:
            return "**Moderate cost efficiency** - Acceptable for difficult areas."
        else:
            return "**High cost per building** - Consider alternatives or verify benefits."
    
    def _extract_warnings(self, context: Dict[str, Any]) -> list[str]:
        """Extract warnings from context."""
        warnings = []
        
        constraints = context.get('constraints', {})
        
        # Boundary warnings
        if constraints.get('boundary') != 'valid':
            warnings.append('Location is outside village boundary')
        
        # Land type warnings
        land_type = constraints.get('land_type', '')
        if land_type == 'private':
            warnings.append('Located on private land - acquisition may be required')
        elif land_type == 'restricted':
            warnings.append('Located on restricted land - placement not recommended')
        
        # Water proximity warnings
        water_distance = constraints.get('water_distance', 999)
        if water_distance < 10:
            warnings.append('Too close to water body (< 10m) - critical violation')
        elif water_distance < 30:
            warnings.append('Close to water body (< 30m) - proceed with caution')
        
        # Road access warnings
        road_distance = constraints.get('road_distance', 999)
        if road_distance > 200:
            warnings.append('Far from roads (> 200m) - access may be challenging')
        
        # Cost warnings
        cost_per_building = context.get('cost_per_building', 0)
        if cost_per_building > 6000:
            warnings.append(f'High cost per building (₹{cost_per_building:,}) - verify benefits justify cost')
        
        return warnings
    
    def _format_warnings(self, context: Dict[str, Any]) -> str:
        """Format warnings section."""
        warnings = self._extract_warnings(context)
        
        if not warnings:
            return "## Warnings\n\nNo significant concerns identified."
        
        warning_list = '\n'.join([f'- {w}' for w in warnings])
        return f"## Warnings\n\n{warning_list}"
    
    def _extract_alternatives(self, context: Dict[str, Any]) -> Optional[str]:
        """Extract information about alternative locations."""
        alternatives = context.get('alternatives', [])
        
        if not alternatives:
            return None
        
        if len(alternatives) == 1:
            return f"1 alternative location scores {alternatives[0].get('score', 0):.1f}/100"
        else:
            return f"{len(alternatives)} alternative locations available with similar scores"
    
    def _format_alternatives(self, context: Dict[str, Any]) -> str:
        """Format alternatives section."""
        alternatives_text = self._extract_alternatives(context)
        
        if not alternatives_text:
            return "## Alternatives\n\nNo comparable alternatives identified in analysis."
        
        return f"## Alternatives\n\n{alternatives_text}"
    
    def _score_to_rating(self, score: float) -> str:
        """Convert numeric score to rating."""
        if score >= 95:
            return 'Excellent'
        elif score >= 85:
            return 'Very Good'
        elif score >= 70:
            return 'Good'
        elif score >= 50:
            return 'Fair'
        else:
            return 'Poor'
