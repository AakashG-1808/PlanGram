"""Generate insights from analysis results."""

from typing import Dict, Any, List


class InsightGenerator:
    """Generate actionable insights from infrastructure analysis."""
    
    def __init__(self, ai_provider=None):
        """
        Initialize insight generator.
        
        Args:
            ai_provider: Optional AI provider for enhanced insights
        """
        self.ai_provider = ai_provider
    
    async def generate(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate insights from analysis results.
        
        Args:
            analysis_results: Coverage analysis data
            
        Returns:
            List of insights with type, title, description, action, impact
        """
        # Try AI provider first if available
        if self.ai_provider:
            try:
                insights = await self.ai_provider.generate_insights(analysis_results)
                if insights:
                    return insights
            except Exception:
                # Fall through to rule-based insights
                pass
        
        # Fallback to rule-based insights
        return self._generate_rule_based_insights(analysis_results)
    
    def _generate_rule_based_insights(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights using rule-based logic."""
        insights = []
        
        # Extract key metrics
        coverage_percent = analysis_results.get('coverage_percent', 0)
        total_buildings = analysis_results.get('total_buildings', 0)
        served_buildings = analysis_results.get('served_buildings', 0)
        unserved_buildings = total_buildings - served_buildings
        
        clusters = analysis_results.get('clusters', [])
        high_priority_count = analysis_results.get('high_priority_count', 0)
        medium_priority_count = analysis_results.get('medium_priority_count', 0)
        
        # Insight 1: Overall coverage assessment
        insights.append(self._coverage_insight(coverage_percent, unserved_buildings))
        
        # Insight 2: Cluster analysis
        if clusters:
            insights.append(self._cluster_insight(clusters))
        
        # Insight 3: Priority areas
        if high_priority_count > 0:
            insights.append(self._priority_insight(high_priority_count, medium_priority_count))
        
        # Insight 4: Fragmentation warning
        if len(clusters) > 5:
            insights.append(self._fragmentation_insight(len(clusters)))
        
        # Insight 5: Optimization opportunity
        if coverage_percent < 80 and len(clusters) <= 3:
            insights.append(self._optimization_insight(unserved_buildings, len(clusters)))
        
        return insights
    
    def _coverage_insight(self, coverage_percent: float, unserved_buildings: int) -> Dict[str, Any]:
        """Generate insight about overall coverage."""
        
        if coverage_percent < 40:
            return {
                'type': 'critical',
                'title': 'Critical Infrastructure Gap Identified',
                'description': (
                    f'Only {coverage_percent:.1f}% of buildings have adequate infrastructure access, '
                    f'leaving {unserved_buildings} buildings underserved.'
                ),
                'action': 'Prioritize immediate infrastructure expansion to underserved areas',
                'impact': f'Strategic placement could serve {unserved_buildings} additional buildings'
            }
        elif coverage_percent < 60:
            return {
                'type': 'critical',
                'title': 'Significant Coverage Gaps Detected',
                'description': (
                    f'Current coverage of {coverage_percent:.1f}% indicates substantial infrastructure gaps '
                    f'affecting {unserved_buildings} buildings.'
                ),
                'action': 'Develop multi-facility plan to achieve 80%+ coverage target',
                'impact': f'Could improve coverage by {100 - coverage_percent:.1f}% with strategic placement'
            }
        elif coverage_percent < 80:
            return {
                'type': 'opportunity',
                'title': 'Moderate Coverage with Improvement Potential',
                'description': (
                    f'Village has {coverage_percent:.1f}% coverage, with {unserved_buildings} buildings '
                    f'still lacking adequate access.'
                ),
                'action': 'Target remaining gaps with 1-2 strategic facilities',
                'impact': 'Could achieve 90%+ coverage with targeted investments'
            }
        else:
            return {
                'type': 'opportunity',
                'title': 'Strong Coverage with Minor Gaps',
                'description': (
                    f'Village has good coverage at {coverage_percent:.1f}%, with only {unserved_buildings} '
                    f'buildings remaining underserved.'
                ),
                'action': 'Address remaining gaps with small-scale solutions',
                'impact': 'Could achieve near-complete coverage with minimal investment'
            }
    
    def _cluster_insight(self, clusters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insight about underserved clusters."""
        
        # Find largest cluster
        largest_cluster = max(clusters, key=lambda c: c.get('building_count', 0))
        cluster_size = largest_cluster.get('building_count', 0)
        cluster_priority = largest_cluster.get('priority', 'unknown')
        
        if cluster_size > 50:
            return {
                'type': 'critical',
                'title': 'Large Underserved Cluster Requires Attention',
                'description': (
                    f'A cluster of {cluster_size} buildings has {cluster_priority.lower()} priority for '
                    f'infrastructure access, representing a significant coverage gap.'
                ),
                'action': 'Prioritize facility placement near this cluster center',
                'impact': f'Single facility could serve {cluster_size}+ buildings simultaneously'
            }
        elif cluster_size > 20:
            return {
                'type': 'opportunity',
                'title': 'Medium Cluster Offers High-Impact Opportunity',
                'description': (
                    f'An underserved cluster of {cluster_size} buildings presents an efficient opportunity '
                    f'for targeted infrastructure placement.'
                ),
                'action': 'Consider this cluster for first-phase implementation',
                'impact': f'Cost-efficient solution serving {cluster_size} buildings with one facility'
            }
        else:
            return {
                'type': 'opportunity',
                'title': 'Multiple Small Clusters Identified',
                'description': (
                    f'Analysis identified {len(clusters)} underserved clusters with {cluster_size} buildings '
                    f'in the largest group.'
                ),
                'action': 'Use hybrid optimization to find locations serving multiple clusters',
                'impact': 'Strategic placement could serve several clusters simultaneously'
            }
    
    def _priority_insight(self, high_priority: int, medium_priority: int) -> Dict[str, Any]:
        """Generate insight about priority areas."""
        
        if high_priority > 0:
            return {
                'type': 'critical',
                'title': f'{high_priority} High-Priority Areas Identified',
                'description': (
                    f'{high_priority} areas have critically low infrastructure coverage (< 50%), '
                    f'requiring immediate attention.'
                ),
                'action': 'Focus initial infrastructure investments on high-priority areas',
                'impact': 'Addresses most urgent needs and maximizes social impact'
            }
        else:
            return {
                'type': 'opportunity',
                'title': f'{medium_priority} Medium-Priority Areas for Improvement',
                'description': (
                    f'{medium_priority} areas have moderate coverage gaps (50-70%), '
                    f'presenting opportunities for targeted improvement.'
                ),
                'action': 'Plan phased implementation starting with medium-priority areas',
                'impact': 'Systematic approach to achieving comprehensive coverage'
            }
    
    def _fragmentation_insight(self, num_clusters: int) -> Dict[str, Any]:
        """Generate insight about fragmented coverage."""
        
        return {
            'type': 'warning',
            'title': 'Highly Fragmented Coverage Pattern Detected',
            'description': (
                f'{num_clusters} separate underserved clusters indicate dispersed infrastructure needs '
                f'across the village.'
            ),
            'action': 'Plan multi-facility strategy or increase budget allocation',
            'impact': 'Complete coverage will require multiple facilities and phased implementation'
        }
    
    def _optimization_insight(self, unserved_buildings: int, num_clusters: int) -> Dict[str, Any]:
        """Generate insight about optimization opportunity."""
        
        return {
            'type': 'opportunity',
            'title': 'Excellent Optimization Potential Identified',
            'description': (
                f'{unserved_buildings} unserved buildings concentrated in {num_clusters} clusters '
                f'creates efficient optimization opportunities.'
            ),
            'action': 'Run budget optimization to find ideal facility placement and quantity',
            'impact': f'High probability of serving {unserved_buildings}+ buildings within budget constraints'
        }
    
    def format_insights(self, insights: List[Dict[str, Any]]) -> str:
        """
        Format insights as human-readable text.
        
        Args:
            insights: List of insight dictionaries
            
        Returns:
            Formatted text
        """
        if not insights:
            return "No insights generated."
        
        output = []
        
        # Group by type
        critical = [i for i in insights if i['type'] == 'critical']
        opportunities = [i for i in insights if i['type'] == 'opportunity']
        warnings = [i for i in insights if i['type'] == 'warning']
        
        if critical:
            output.append("## Critical Issues\n")
            for insight in critical:
                output.append(self._format_insight(insight))
        
        if opportunities:
            output.append("## Opportunities\n")
            for insight in opportunities:
                output.append(self._format_insight(insight))
        
        if warnings:
            output.append("## Warnings\n")
            for insight in warnings:
                output.append(self._format_insight(insight))
        
        return '\n'.join(output)
    
    def _format_insight(self, insight: Dict[str, Any]) -> str:
        """Format a single insight."""
        return f"""### {insight['title']}

**Description:** {insight['description']}

**Recommended Action:** {insight['action']}

**Expected Impact:** {insight['impact']}

"""
