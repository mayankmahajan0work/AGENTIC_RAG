"""
Main ingestion script - Loads all data into vector stores.

Run this script to:
1. Load schema data into schema_knowledge collection
2. Load validation rules into validation_rules collection

This only needs to be run once (or when data changes).
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import from other modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.load_schema import create_schema_index
from ingestion.load_rules import create_rules_index


def ingest_all_data():
    """
    Load both schema and validation rules into Chroma.
    
    This is the main function to set up all your vector stores.
    """
    print("=" * 60)
    print("🔄 INGESTING ALL DATA INTO VECTOR STORES")
    print("=" * 60)
    
    try:
        # Load schema
        print("\n📊 STEP 1: Loading Schema Data")
        print("-" * 60)
        create_schema_index()
        
        # Load validation rules
        print("\n📋 STEP 2: Loading Validation Rules")
        print("-" * 60)
        create_rules_index()
        
        print("\n" + "=" * 60)
        print("✅ ALL DATA INGESTED SUCCESSFULLY!")
        print("=" * 60)
        print("\nYour vector stores are ready. You can now:")
        print("  1. Run queries against the data")
        print("  2. Start the Streamlit UI")
        print("  3. Test retrieval")
        
    except Exception as e:
        print(f"\n❌ Error during ingestion: {e}")
        raise


if __name__ == "__main__":
    ingest_all_data()
