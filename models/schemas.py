"""
Data models using Pydantic for validation.

These are like templates that ensure our data has the right shape and types.
Pydantic will automatically check and validate data for us!
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    """User's question coming into the system"""
    query: str = Field(..., min_length=1, description="The user's question")
    
    class Config:
        # Example for documentation
        json_schema_extra = {
            "example": {
                "query": "What validations apply to claims data?"
            }
        }


class RetrievedDocument(BaseModel):
    """A single document retrieved from the vector store"""
    content: str = Field(..., description="The actual text content")
    metadata: dict = Field(default_factory=dict, description="Extra info about the document")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")


class QueryResponse(BaseModel):
    """The response we send back to the user"""
    query: str = Field(..., description="Original user question")
    intent: str = Field(..., description="Detected intent type")
    response: str = Field(..., description="AI-generated answer")
    sql_queries: List[str] = Field(default_factory=list, description="Generated SQL queries")
    retrieved_docs: List[RetrievedDocument] = Field(
        default_factory=list, 
        description="Documents used to answer"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Generate SQL to validate claims",
                "intent": "sql",
                "response": "Here are validation queries...",
                "sql_queries": ["SELECT * FROM claims WHERE amount <= 0"],
                "retrieved_docs": []
            }
        }


class SchemaTable(BaseModel):
    """Represents a database table from our schema"""
    table_name: str
    description: str
    columns: List[dict]
    relationships: List[str] = Field(default_factory=list)


class ValidationRule(BaseModel):
    """Represents a validation rule"""
    rule_id: str
    rule_name: str
    rule_type: str  # "data_quality" or "business_rule"
    description: str
    sql_validation: str
    severity: str
    affected_tables: List[str] = Field(default_factory=list)
