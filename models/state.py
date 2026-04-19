"""
State schema for LangGraph workflow.

This defines what information flows through our agent workflow.
Think of it as a shared notebook that each step in the workflow can read and write to.
"""

from typing import TypedDict, List, Optional


class GraphState(TypedDict):
    """
    The state that gets passed between nodes in our LangGraph workflow.
    
    Each field represents data that flows through the system:
    - Input from user
    - Decisions made by agents
    - Retrieved context
    - Final output
    """
    
    # User's original question
    query: str
    
    # What type of question is this? (decided by router agent)
    # Options: "schema", "validation", "sql", "relationship"
    intent: Optional[str]
    
    # Documents retrieved from vector store
    # Each document has content and metadata
    retrieved_context: List[dict]
    
    # The final answer we give back to user
    response: str
    
    # Any SQL queries we generated
    sql_queries: List[str]
    
    # Extra info for debugging or tracking
    metadata: dict
