"""
Data models and state schemas for the application.

This module contains:
- GraphState: LangGraph state (what flows through the workflow)
- Pydantic models: For data validation (QueryRequest, QueryResponse, etc.)
- Enums: Constants like IntentType, RuleType, Severity
"""

# State for LangGraph workflow
from models.state import GraphState

# Data validation models
from models.schemas import (
    QueryRequest,
    QueryResponse,
    RetrievedDocument,
    SchemaTable,
    ValidationRule,
)

# Enums and constants
from models.enums import (
    IntentType,
    RuleType,
    Severity,
    CollectionName,
    DEFAULT_SYSTEM_PROMPT,
    MAX_CONTEXT_LENGTH,
    DEFAULT_TOP_K,
)

# Make everything easy to import
__all__ = [
    # State
    "GraphState",
    # Models
    "QueryRequest",
    "QueryResponse",
    "RetrievedDocument",
    "SchemaTable",
    "ValidationRule",
    # Enums
    "IntentType",
    "RuleType",
    "Severity",
    "CollectionName",
    # Constants
    "DEFAULT_SYSTEM_PROMPT",
    "MAX_CONTEXT_LENGTH",
    "DEFAULT_TOP_K",
]
