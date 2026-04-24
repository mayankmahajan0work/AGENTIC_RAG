# Agentic RAG for Data Engineering and ETL

Capstone project demonstrating a simple multi-index RAG system with a router agent.

The app accepts a user question, classifies the intent, routes the question to the correct Chroma index, retrieves relevant context, and generates a final answer or SQL query.

## Overview

This project is built to show three ideas clearly:

- multi-index RAG using two separate vector indexes
- agentic routing with LangGraph
- SQL generation grounded in retrieved schema and rule context

The demo uses healthcare claims data, but the architecture is intentionally small and easy to explain.

## What the System Does

The system supports three user intents:

- `schema`: questions about tables, columns, and relationships
- `validation`: questions about business rules and data quality checks
- `sql`: requests to generate SQL queries

It uses two Chroma collections:

- `schema_knowledge`: schema definitions, columns, and table relationships
- `validation_rules`: rule descriptions, validation logic, and sample SQL checks

Routing behavior:

- `schema` queries go to the schema index
- `validation` queries go to the rules index
- `sql` queries retrieve from both indexes

## End-to-End Flow

```text
User Query
   ↓
Router Agent (classify intent)
   ↓
Retriever
   ├─ schema index
   ├─ rules index
   └─ or both
   ↓
Response Generator
   ↓
Final Answer / SQL
```

## Tech Stack

- LangGraph
- ChromaDB
- OpenAI `gpt-4o-mini`
- OpenAI `text-embedding-3-small`
- Streamlit
- Python 3.11+

## Repository Structure

```text
AGENTIC_RAG/
├── agents/              # Router and response generation
├── config/              # Environment and project settings
├── data/input/          # Demo schema and validation rules JSON
├── evaluation/          # Optional RAGAS evaluation scripts
├── ingestion/           # Load JSON into Chroma collections
├── models/              # State and intent definitions
├── retriever/           # Chroma access and retrieval logic
├── workflows/           # LangGraph nodes and graph builder
├── app.py               # Streamlit app
├── main.py              # CLI entry point
└── tests.py             # Smoke and workflow test script
```

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install uv
uv pip install -e .
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Add your OpenAI API key to `.env`:

```env
OPENAI_API_KEY=your_api_key_here
```

### 4. Ingest the demo data

```bash
python ingestion/ingest_data.py
```

This creates the two Chroma collections used by the app.

## Run the App

Start the Streamlit interface:

```bash
streamlit run app.py
```

Then open `http://localhost:8501`.

You can also run the CLI version:

```bash
python main.py
```

## Example Questions

Schema:

- `What columns are in the claims table?`
- `How do I join claims with members?`

Validation:

- `How do I check for duplicate claims?`
- `What are the data quality rules for claims?`

SQL:

- `Write SQL to find all claims with billed_amount > 5000`
- `Find members who have multiple claims on the same service date`

## Why This Is a Good Capstone

This project stays at a good capstone level because it is:

- small enough to explain in a short presentation
- practical enough to demonstrate real RAG design choices
- structured enough to show agentic routing instead of a single-index chatbot

It demonstrates:

- separating knowledge into multiple indexes
- choosing retrieval paths based on query intent
- using LangGraph for a simple decision workflow
- grounding SQL generation in retrieved context
- showing retrieved sources in the UI

## Testing

Run the smoke and workflow tests:

```bash
python tests.py
```

Run specific groups:

```bash
python tests.py --agents
python tests.py --retriever
python tests.py --workflow
```

## Optional Evaluation

RAGAS evaluation is kept optional so the main project stays lightweight.

Install evaluation dependencies:

```bash
pip install -e .[evaluation]
```

Run evaluation:

```bash
cd evaluation
python ragas_eval.py
```

Current reported results:

- Context Precision: `0.842`
- Answer Relevancy: `0.686`
- Faithfulness: `0.671`
- Success Rate: `100%` on 19 test queries

## Adapting the Project

To reuse this project with another domain:

1. Replace the JSON files in `data/input/`
2. Keep one file for schema knowledge and one for business or validation rules
3. Re-run ingestion
4. Test the same routing flow in the app

This makes it easy to swap the demo domain without changing the overall architecture.

## Future Improvements

- execute generated SQL against a sample database
- add guardrails for SQL validation
- improve retrieval with hybrid search
- support uploaded documents instead of only JSON input
- add conversation memory if multi-turn behavior is needed

## License

MIT
