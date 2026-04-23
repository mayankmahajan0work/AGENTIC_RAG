"""
Data models and state schemas for the application.

This module contains:
- GraphState: LangGraph state (what flows through the workflow)
- Enums: IntentType for routing logic
"""

# State for LangGraph workflow
from models.state import GraphState

# Enums
from models.enums import IntentType

# Make everything easy to import
__all__ = [
    "GraphState",
    "IntentType"
]
