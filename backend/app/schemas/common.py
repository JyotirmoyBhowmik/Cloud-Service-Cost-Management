"""
Common API Schemas & DTOs
Complies with Rule 1.2 (Strict Schema Enforcement), Rule 2.4 (Sanitized Error Responses), and Rule 5.2 (Pagination).
"""

from typing import Generic, TypeVar, List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total_count: int = Field(ge=0, description="Total number of items matching filters")
    page: int = Field(ge=1, description="Current 1-indexed page")
    page_size: int = Field(ge=1, le=500, description="Items per page")
    total_pages: int = Field(ge=0, description="Total pages available")


class StandardErrorResponse(BaseModel):
    timestamp: str
    status_code: int
    error_code: str
    correlation_id: str
    message: str
    details: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    message: str
    success: bool = True
