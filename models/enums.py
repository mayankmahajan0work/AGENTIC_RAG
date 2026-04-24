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
    SCHEMA = "schema"              # Questions about database structure and relationships
    VALIDATION = "validation"      # Questions about validation rules
    SQL_GENERATION = "sql"         # Requests to generate SQL queries
