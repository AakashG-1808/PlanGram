"""Intent parser for natural language queries."""

import re
from typing import Dict, Any, Optional


class IntentParser:
    """
    Parse natural language queries into structured intents.
    Falls back to regex-based parsing if AI provider fails.
    """
    
    # Regex patterns for parameter extraction
    VILLAGE_PATTERN = re.compile(r'village[_\s]?(\d+|[a-z_]+)', re.IGNORECASE)
    BUDGET_PATTERN = re.compile(r'(?:budget|cost|funds?).*?(\d+(?:,?\d+)*)', re.IGNORECASE)
    THRESHOLD_PATTERN = re.compile(r'(?:threshold|distance|radius).*?(\d+)', re.IGNORECASE)
    INFRA_PATTERN = re.compile(r'\b(water|waste|health|education)\b', re.IGNORECASE)
    NUM_PATTERN = re.compile(r'(\d+)\s+(?:candidate|location|facilit)', re.IGNORECASE)
    METHOD_PATTERN = re.compile(r'\b(grid|gap|hybrid)\b', re.IGNORECASE)
    COORDS_PATTERN = re.compile(r'([\d.]+)\s*,\s*([\d.]+)')
    
    # Action keywords
    ACTION_KEYWORDS = {
        'optimize': ['optimize', 'best', 'optimal', 'find location', 'recommend'],
        'analyze': ['analyze', 'coverage', 'metrics', 'statistics'],
        'validate': ['validate', 'check location', 'verify'],
        'generate_candidates': ['generate', 'candidate', 'suggest location'],
        'compare_scenarios': ['compare', 'scenario', 'comparison'],
    }
    
    def __init__(self, ai_provider=None):
        """
        Initialize intent parser.
        
        Args:
            ai_provider: Optional AI provider for enhanced parsing
        """
        self.ai_provider = ai_provider
    
    async def parse(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Parse natural language query into structured intent.
        
        Args:
            query: User's natural language query
            context: Additional context (available villages, etc.)
            
        Returns:
            Structured intent dictionary
        """
        context = context or {}
        
        # Try AI provider first if available
        if self.ai_provider:
            try:
                intent = await self.ai_provider.parse_intent(query, context)
                if intent.get('action') != 'error':
                    return intent
            except Exception:
                # Fall through to regex-based parsing
                pass
        
        # Fallback to regex-based parsing
        return self._parse_with_regex(query, context)
    
    def _parse_with_regex(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse query using regex patterns."""
        intent = {'original_query': query}
        
        # Detect action
        action = self._detect_action(query)
        if action:
            intent['action'] = action
        else:
            intent['action'] = 'error'
            intent['error'] = 'Could not determine action from query'
            return intent
        
        # Extract village ID
        village_match = self.VILLAGE_PATTERN.search(query)
        if village_match:
            intent['village_id'] = f"village_{village_match.group(1)}" if village_match.group(1).isdigit() else village_match.group(1)
        
        # Extract infrastructure type
        infra_match = self.INFRA_PATTERN.search(query)
        if infra_match:
            intent['infrastructure_type'] = infra_match.group(1).lower()
        
        # Extract budget
        budget_match = self.BUDGET_PATTERN.search(query)
        if budget_match:
            budget_str = budget_match.group(1).replace(',', '')
            intent['budget'] = int(budget_str)
        
        # Extract threshold
        threshold_match = self.THRESHOLD_PATTERN.search(query)
        if threshold_match:
            intent['threshold'] = int(threshold_match.group(1))
        else:
            intent['threshold'] = 500  # Default
        
        # Extract number of candidates
        num_match = self.NUM_PATTERN.search(query)
        if num_match:
            intent['num_candidates'] = int(num_match.group(1))
        
        # Extract method
        method_match = self.METHOD_PATTERN.search(query)
        if method_match:
            intent['method'] = method_match.group(1).lower()
        else:
            intent['method'] = 'hybrid'  # Default
        
        # Extract coordinates for validation queries
        coords_match = self.COORDS_PATTERN.search(query)
        if coords_match and action == 'validate':
            intent['lat'] = float(coords_match.group(1))
            intent['lng'] = float(coords_match.group(2))
        
        return intent
    
    def _detect_action(self, query: str) -> Optional[str]:
        """Detect action type from query."""
        query_lower = query.lower()
        
        for action, keywords in self.ACTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return action
        
        return None
    
    def validate_intent(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate intent has required parameters for its action.
        
        Args:
            intent: Parsed intent dictionary
            
        Returns:
            Validated intent with error field if invalid
        """
        action = intent.get('action')
        
        if action == 'error':
            return intent
        
        errors = []
        
        # Validate required parameters per action
        if action in ['optimize', 'analyze', 'generate_candidates']:
            if 'village_id' not in intent:
                errors.append('village_id required')
        
        if action == 'optimize':
            if 'infrastructure_type' not in intent:
                errors.append('infrastructure_type required')
            if 'budget' not in intent:
                errors.append('budget required')
        
        if action == 'generate_candidates':
            if 'infrastructure_type' not in intent:
                errors.append('infrastructure_type required')
        
        if action == 'validate':
            if 'lat' not in intent or 'lng' not in intent:
                errors.append('coordinates (lat, lng) required')
            if 'village_id' not in intent:
                errors.append('village_id required')
        
        if errors:
            intent['action'] = 'error'
            intent['error'] = f"Missing parameters: {', '.join(errors)}"
        
        return intent
