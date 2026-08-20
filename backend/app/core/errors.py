"""
Custom error classes and error handling utilities for PlanGram API
"""

from typing import Any, Optional, Dict
from datetime import datetime
import uuid


class PlanGramError(Exception):
    """Base exception for all PlanGram errors"""
    
    def __init__(
        self, 
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[str] = None,
        status_code: int = 500
    ):
        self.message = message
        self.code = code
        self.details = details
        self.status_code = status_code
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.request_id = str(uuid.uuid4())[:8]
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response"""
        error_dict = {
            "error": {
                "code": self.code,
                "message": self.message,
                "timestamp": self.timestamp,
                "request_id": self.request_id
            }
        }
        if self.details:
            error_dict["error"]["details"] = self.details
        return error_dict


class ValidationError(PlanGramError):
    """Invalid input or parameters"""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=details,
            status_code=400
        )


class NotFoundError(PlanGramError):
    """Resource not found"""
    
    def __init__(self, resource: str, identifier: str, available: Optional[list] = None):
        message = f"{resource} '{identifier}' not found"
        details = None
        if available:
            details = f"Available: {', '.join(available)}"
        
        super().__init__(
            message=message,
            code="NOT_FOUND",
            details=details,
            status_code=404
        )


class ConstraintViolationError(PlanGramError):
    """Business rule or constraint violation"""
    
    def __init__(self, message: str, violations: Optional[list] = None):
        details = None
        if violations:
            details = f"Violations: {', '.join(violations)}"
        
        super().__init__(
            message=message,
            code="CONSTRAINT_VIOLATION",
            details=details,
            status_code=422
        )


class ServiceUnavailableError(PlanGramError):
    """External service unavailable"""
    
    def __init__(self, service: str, reason: Optional[str] = None):
        message = f"{service} service is unavailable"
        details = reason if reason else "Please try again later"
        
        super().__init__(
            message=message,
            code="SERVICE_UNAVAILABLE",
            details=details,
            status_code=503
        )


class ConfigurationError(PlanGramError):
    """Configuration or setup error"""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            details=details,
            status_code=500
        )


class DataError(PlanGramError):
    """Data processing or integrity error"""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            message=message,
            code="DATA_ERROR",
            details=details,
            status_code=500
        )


class OptimizationError(PlanGramError):
    """Optimization algorithm error"""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            message=message,
            code="OPTIMIZATION_ERROR",
            details=details,
            status_code=500
        )


# User-friendly error messages
ERROR_MESSAGES = {
    "VILLAGE_NOT_FOUND": "The village you're looking for doesn't exist in our system.",
    "INVALID_LOCATION": "The location coordinates are invalid or outside the village boundary.",
    "INSUFFICIENT_BUDGET": "The budget provided is insufficient for any facility placement.",
    "NO_CANDIDATES_FOUND": "No suitable candidate locations found. Try adjusting constraints.",
    "OPTIMIZATION_FAILED": "Optimization could not find a solution. Try increasing budget or adjusting parameters.",
    "AI_SERVICE_DOWN": "AI service is temporarily unavailable. Basic features still work.",
    "INVALID_THRESHOLD": "Distance threshold must be between 100 and 1000 meters.",
    "DATA_FILE_MISSING": "Required data file is missing. Please contact administrator.",
}


def get_user_friendly_message(code: str, default: str = None) -> str:
    """Get user-friendly error message for error code"""
    return ERROR_MESSAGES.get(code, default or "An unexpected error occurred.")
