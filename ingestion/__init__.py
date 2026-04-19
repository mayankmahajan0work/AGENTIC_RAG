"""
Data ingestion module for loading schema and validation rules into vector stores.

Usage:
    # Load all data at once
    from ingestion import ingest_all_data
    ingest_all_data()
    
    # Or load individually
    from ingestion import create_schema_index, create_rules_index
    create_schema_index()
    create_rules_index()
"""

from ingestion.load_schema import create_schema_index
from ingestion.load_rules import create_rules_index
from ingestion.ingest_data import ingest_all_data

__all__ = [
    "create_schema_index",
    "create_rules_index",
    "ingest_all_data",
]
