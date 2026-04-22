"""
Response Generator - Creates SQL queries and answers using LLM.

This agent takes the user's query and retrieved context,
then generates appropriate SQL queries or explanations.
"""

from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from models.enums import IntentType
from config import settings


# System prompts for different intent types
SCHEMA_PROMPT = """You are a healthcare claims database expert. 
The user asked about database schema/structure.

CRITICAL INSTRUCTIONS:
- ONLY use information from the retrieved schema context below
- DO NOT make up or assume any columns, tables, or relationships that aren't explicitly shown
- If the schema doesn't contain the information needed to answer the question, clearly state what's missing

Retrieved Schema Context:
{context}

User Question: {query}

Provide a helpful answer about the database structure using ONLY the information above."""


VALIDATION_PROMPT = """You are a data quality expert for healthcare claims.
The user asked about validation rules or data quality checks.

CRITICAL INSTRUCTIONS:
- ONLY use information from the retrieved validation rules below
- DO NOT create or modify SQL queries beyond what's provided
- If the rules don't cover what the user asked, clearly state that

Retrieved Validation Rules:
{context}

User Question: {query}

Provide a clear explanation using ONLY the rules above. Include:
1. What the rule checks for
2. The SQL query to validate (exactly as provided)
3. What the expected result should be
4. How to fix issues if found"""


SQL_GENERATION_PROMPT = """Generate SQL using ONLY the schema below.

Schema:
{schema_context}

(Validation rules for reference: {rules_context})

User Request: {query}

RULES:
- READ the schema carefully - check ALL tables and their columns
- If columns exist (even in different tables), write the SQL with JOINs
- Look for "Relationships:" to find foreign keys  
- Keep SQL simple and correct
- Only say "Cannot generate" if columns truly don't exist

EXAMPLES:

Request: "Find claims over 1000"
Schema has: claims table with billed_amount column
SQL:
```sql
SELECT * FROM claims WHERE billed_amount > 1000;
```

Request: "Show claims with member names" 
Schema has: claims (member_id), members (member_id, first_name, last_name), Relationship: claims.member_id → members.member_id
SQL:
```sql
SELECT c.*, m.first_name, m.last_name
FROM claims c
JOIN members m ON c.member_id = m.member_id;
```

Request: "Find diagnosis D0.2"
Schema has: claim_lines table with diagnosis_code column
SQL:
```sql
SELECT * FROM claim_lines WHERE diagnosis_code = 'D0.2';
```

Generate SQL now."""


RELATIONSHIP_PROMPT = """You are a database relationship expert for healthcare claims.
The user asked about how tables relate to each other.

CRITICAL INSTRUCTIONS:
- ONLY describe relationships explicitly shown in the schema below
- DO NOT assume or create relationships that aren't documented
- Only reference columns that actually exist in the tables

Schema Information:
{context}

User Question: {query}

Explain the relationships clearly using ONLY the information above:
1. Which tables are involved
2. The foreign key relationships (as documented)
3. How to join them in SQL (using only existing columns)
4. Sample join syntax

If the schema doesn't show the relationships the user asked about, clearly state that."""


def format_context(documents: List[Dict[str, Any]]) -> str:
    """
    Format retrieved documents into readable context string.
    
    Args:
        documents: List of document dictionaries from retriever
    
    Returns:
        Formatted context string
    """
    if not documents:
        return "No relevant information found."
    
    context_parts = []
    for i, doc in enumerate(documents, 1):
        context_parts.append(f"--- Document {i} ---")
        context_parts.append(doc['content'])
        context_parts.append("")  # Empty line
    
    return "\n".join(context_parts)


def generate_response(
    query: str,
    intent: IntentType,
    schema_docs: List[Dict[str, Any]] = None,
    rules_docs: List[Dict[str, Any]] = None
) -> str:
    """
    Generate response based on intent and retrieved context.
    
    Args:
        query: The user's question
        intent: Classified intent type
        schema_docs: Retrieved schema documents
        rules_docs: Retrieved validation rule documents
    
    Returns:
        Generated response (explanation or SQL query)
    """
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=0.1  # Mostly deterministic but slightly flexible
    )
    
    # Select prompt based on intent
    if intent == IntentType.SCHEMA:
        context = format_context(schema_docs or [])
        prompt_template = SCHEMA_PROMPT
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"context": context, "query": query})
        
    elif intent == IntentType.VALIDATION:
        context = format_context(rules_docs or [])
        prompt_template = VALIDATION_PROMPT
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"context": context, "query": query})
        
    elif intent == IntentType.SQL_GENERATION:
        schema_context = format_context(schema_docs or [])
        rules_context = format_context(rules_docs or [])
        prompt_template = SQL_GENERATION_PROMPT
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({
            "schema_context": schema_context,
            "rules_context": rules_context,
            "query": query
        })
        
    elif intent == IntentType.RELATIONSHIP:
        context = format_context(schema_docs or [])
        prompt_template = RELATIONSHIP_PROMPT
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"context": context, "query": query})
        
    else:
        response = "I'm not sure how to answer that question. Please rephrase or ask about schema, validation rules, or SQL queries."
    
    return response


def generate_sql_only(
    query: str,
    schema_docs: List[Dict[str, Any]],
    rules_docs: List[Dict[str, Any]] = None
) -> str:
    """
    Generate ONLY SQL query without explanations.
    
    Simplified version for when you just want the SQL.
    
    Args:
        query: What SQL to generate
        schema_docs: Schema information
        rules_docs: Optional validation rules for reference
    
    Returns:
        SQL query string
    """
    return generate_response(
        query=query,
        intent=IntentType.SQL_GENERATION,
        schema_docs=schema_docs,
        rules_docs=rules_docs
    )
