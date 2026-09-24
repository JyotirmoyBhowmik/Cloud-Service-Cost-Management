"""
Domain Exceptions & Error Mappings
Complies with Rule 2.2 (Domain Exceptions) and Rule 2.4 (Sanitized Error Responses).
"""

from typing import Optional, Dict, Any


class CloudScopeException(Exception):
    """Base domain exception for all CloudScope business logic errors."""
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}


class EntityNotFoundException(CloudScopeException):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            message=f"{entity_name} with identifier '{entity_id}' was not found.",
            error_code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"entity_name": entity_name, "entity_id": entity_id},
        )


class DuplicateEntityException(CloudScopeException):
    def __init__(self, entity_name: str, field_name: str, value: str):
        super().__init__(
            message=f"{entity_name} with {field_name}='{value}' already exists.",
            error_code="DUPLICATE_ENTITY",
            status_code=409,
            details={"entity_name": entity_name, "field": field_name, "value": value},
        )


class AuthenticationFailedException(CloudScopeException):
    def __init__(self, message: str = "Invalid credentials or expired session token."):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_FAILED",
            status_code=401,
        )


class InsufficientPermissionsException(CloudScopeException):
    def __init__(self, required_permission: str):
        super().__init__(
            message=f"Access denied. Missing required permission: {required_permission}",
            error_code="FORBIDDEN_ACCESS",
            status_code=403,
            details={"required_permission": required_permission},
        )


class ValidationDomainException(CloudScopeException):
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="INPUT_VALIDATION_ERROR",
            status_code=422,
            details={"field": field} if field else {},
        )


class ProviderAPIException(CloudScopeException):
    def __init__(self, provider: str, operation: str, reason: str, status_code: int = 502):
        super().__init__(
            message=f"Cloud provider '{provider}' API error during {operation}: {reason}",
            error_code="PROVIDER_INTEGRATION_ERROR",
            status_code=status_code,
            details={"provider": provider, "operation": operation},
        )


class CircuitBreakerOpenException(CloudScopeException):
    def __init__(self, provider: str):
        super().__init__(
            message=f"Circuit breaker is OPEN for provider '{provider}'. Upstream calls temporarily halted.",
            error_code="CIRCUIT_BREAKER_ACTIVE",
            status_code=503,
            details={"provider": provider},
        )


class PricingNotAvailableException(CloudScopeException):
    def __init__(self, provider: str, service: str, sku: str):
        super().__init__(
            message=f"Pricing SKU '{sku}' for service '{service}' on provider '{provider}' is not available in catalog.",
            error_code="PRICING_CATALOG_MISSING",
            status_code=404,
            details={"provider": provider, "service": service, "sku": sku},
        )


class ThresholdBreachException(CloudScopeException):
    def __init__(self, resource_name: str, metric: str, value: float, threshold: float):
        super().__init__(
            message=f"Threshold breached on {resource_name}: {metric} value {value} exceeds {threshold}.",
            error_code="THRESHOLD_BREACH",
            status_code=400,
            details={"resource": resource_name, "metric": metric, "value": value, "threshold": threshold},
        )
