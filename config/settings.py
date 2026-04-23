"""
Settings for the application - All configuration in one simple place!
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the base directory of the project (where this file's parent is)
BASE_DIR = Path(__file__).parent.parent

# =============================================================================
# API KEYS (from .env file)
# =============================================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Optional: LangSmith for debugging (can be None)
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")


# =============================================================================
# LLM SETTINGS - Which model to use and how it behaves
# =============================================================================
LLM_MODEL = "gpt-4o-mini"  # The AI model we'll use
LLM_MAX_TOKENS = 2000      # Maximum length of AI responses


# =============================================================================
# EMBEDDING SETTINGS - For converting text to vectors
# =============================================================================
EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI embedding model
EMBEDDING_DIMENSIONS = 1536                 # Size of embedding vectors


# =============================================================================
# VECTOR DATABASE SETTINGS - Where we store our indexes
# =============================================================================
CHROMA_DB_DIR = BASE_DIR / "chroma_db"           # Where Chroma saves data
SCHEMA_COLLECTION = "schema_knowledge"            # Name for schema index
RULES_COLLECTION = "validation_rules"             # Name for rules index
RETRIEVAL_TOP_K = 5                               # How many results to retrieve


# =============================================================================
# FILE PATHS - Where our data files are located
# =============================================================================
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"

SCHEMA_FILE = INPUT_DIR / "claims_schema.json"
RULES_FILE = INPUT_DIR / "validation_rules.json"


# =============================================================================
# CHECK EVERYTHING IS SETUP CORRECTLY
# =============================================================================
def validate_settings():
    """Check that all required files and directories exist"""
    
    # Create directories if they don't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check API key exists
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY not found! Please add it to your .env file"
        )
    
    # Check data files exist
    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(
            f"Schema file not found at: {SCHEMA_FILE}\n"
            "Make sure claims_schema.json is in data/input/"
        )
    
    if not RULES_FILE.exists():
        raise FileNotFoundError(
            f"Rules file not found at: {RULES_FILE}\n"
            "Make sure validation_rules.json is in data/input/"
        )
    
    print("✅ All settings validated successfully!")


# Run validation when this module is imported
validate_settings()
