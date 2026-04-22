"""
Router Agent - Classifies user query intent.

This agent determines what type of question the user is asking
so we know which retrieval strategy to use.
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from models.enums import IntentType
from config import settings


# System prompt for intent classification
ROUTER_SYSTEM_PROMPT = """You are an expert at classifying healthcare claims database queries.

Given a user's question, classify it into ONE of these categories:

1. SCHEMA - Questions about table structure, columns, data types, relationships
   Examples: "What columns are in the claims table?", "How are members and claims related?"

2. VALIDATION - Questions about data quality rules, validation checks, business rules
   Examples: "How do I check for duplicates?", "What are the data quality rules?"

3. SQL_GENERATION - Requests to generate SQL queries for specific analysis
   Examples: "Write SQL to find high-cost claims", "Generate a query for denied claims"

4. RELATIONSHIP - Questions about how tables relate or join together
   Examples: "How do I join claims with providers?", "What's the relationship between members and claims?"

Respond with ONLY the category name: SCHEMA, VALIDATION, SQL_GENERATION, or RELATIONSHIP"""


def classify_intent(query: str) -> IntentType:
    """
    Classify the user's query intent.
    
    Args:
        query: The user's question
    
    Returns:
        IntentType enum value (SCHEMA, VALIDATION, SQL_GENERATION, RELATIONSHIP)
    """
    # Create LLM
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=0  # Deterministic for classification
    )
    
    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", ROUTER_SYSTEM_PROMPT),
        ("human", "{query}")
    ])
    
    # Create chain
    chain = prompt | llm | StrOutputParser()
    
    # Get classification
    result = chain.invoke({"query": query})
    
    # Parse to enum
    result_clean = result.strip().upper()
    
    # Map to IntentType
    intent_mapping = {
        "SCHEMA": IntentType.SCHEMA,
        "VALIDATION": IntentType.VALIDATION,
        "SQL_GENERATION": IntentType.SQL_GENERATION,
        "RELATIONSHIP": IntentType.RELATIONSHIP
    }
    
    return intent_mapping.get(result_clean, IntentType.SCHEMA)  # Default to SCHEMA


def classify_intent_with_reasoning(query: str) -> dict:
    """
    Classify intent and provide reasoning (for debugging/testing).
    
    Args:
        query: The user's question
    
    Returns:
        Dictionary with intent and reasoning
    """
    # Extended prompt with reasoning
    reasoning_prompt = f"""{ROUTER_SYSTEM_PROMPT}

After the category, on a new line, explain why in one sentence.

Format:
CATEGORY
Reason: <your explanation>"""
    
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=0
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", reasoning_prompt),
        ("human", "{query}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"query": query})
    
    # Parse result
    lines = result.strip().split('\n', 1)
    category = lines[0].strip().upper()
    reasoning = lines[1].strip() if len(lines) > 1 else "No reasoning provided"
    
    intent_mapping = {
        "SCHEMA": IntentType.SCHEMA,
        "VALIDATION": IntentType.VALIDATION,
        "SQL_GENERATION": IntentType.SQL_GENERATION,
        "RELATIONSHIP": IntentType.RELATIONSHIP
    }
    
    return {
        "intent": intent_mapping.get(category, IntentType.SCHEMA),
        "reasoning": reasoning,
        "raw_response": result
    }
