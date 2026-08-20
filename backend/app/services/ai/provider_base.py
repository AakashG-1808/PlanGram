"""Abstract base class for AI providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class AIProvider(ABC):
    """Abstract base class for AI providers (Gemini, OpenAI, etc.)"""
    
    @abstractmethod
    async def parse_intent(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse natural language query into structured intent.
        
        Args:
            query: User's natural language query
            context: Additional context (available villages, etc.)
            
        Returns:
            Structured intent with action, parameters
        """
        pass
    
    @abstractmethod
    async def explain_recommendation(
        self, 
        location: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Generate explanation for why a location is recommended.
        
        Args:
            location: Location data (lat, lng, score)
            context: Analysis context (coverage, constraints, costs)
            
        Returns:
            Human-readable explanation
        """
        pass
    
    @abstractmethod
    async def generate_insights(
        self, 
        analysis_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable insights from analysis results.
        
        Args:
            analysis_results: Coverage analysis, clusters, priorities
            
        Returns:
            List of insights with type, title, description, action
        """
        pass
    
    def _format_budget(self, amount: int) -> str:
        """Format currency amount in Indian Rupees."""
        return f"₹{amount:,}"
    
    def _format_percent(self, value: float) -> str:
        """Format percentage with 1 decimal place."""
        return f"{value:.1f}%"
