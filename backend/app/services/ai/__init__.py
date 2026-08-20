"""AI services for natural language processing and explanations."""

from .provider_base import AIProvider
from .provider_gemini import GeminiProvider
from .intent_parser import IntentParser
from .explainer import RecommendationExplainer
from .insights import InsightGenerator

__all__ = [
    'AIProvider',
    'GeminiProvider',
    'IntentParser',
    'RecommendationExplainer',
    'InsightGenerator',
]
