"""
Enums and constants used throughout the application.

Enums help us avoid typos and make our code clearer.
Instead of writing "schema" as a string (easy to mistype), we use IntentType.SCHEMA
"""

from enum import Enum


class IntentType(str, Enum):
    """
    Types of user questions our system can handle.
    
    The router agent will classify each question into one of these types.
    """
    SCHEMA = "schema"              # Questions about database structure
    VALIDATION = "validation"      # Questions about validation rules
    SQL_GENERATION = "sql"         # Requests to generate SQL queries
    RELATIONSHIP = "relationship"  # Questions about table relationships


class RuleType(str, Enum):
    """Types of validation rules"""
    DATA_QUALITY = "data_quality"      # Format, nulls, referential integrity
    BUSINESS_RULE = "business_rule"    # Business logic, policy rules


class Severity(str, Enum):
    """How critical a validation rule is"""
    CRITICAL = "critical"  # Must be fixed immediately
    HIGH = "high"          # Should be fixed soon
    MEDIUM = "medium"      # Nice to fix, for auditing
    LOW = "low"            # Optional, informational


class CollectionName(str, Enum):
    """Names of our Chroma vector store collections"""
    SCHEMA = "schema_knowledge"
    RULES = "validation_rules"


# Constants for prompts and responses
DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant specializing in healthcare claims data validation.
You help users understand database schemas, discover validation rules, and generate SQL queries."""

MAX_CONTEXT_LENGTH = 4000  # Maximum characters of context to send to LLM
DEFAULT_TOP_K = 5          # Default number of results to retrieve
