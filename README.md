🧠 Agentic RAG for Healthcare Claims Data Validation

📌 Project Overview

This project builds an Agentic Retrieval-Augmented Generation (RAG) system specifically for **healthcare payer claims data validation**. It helps data engineers and QA analysts:
	•	Understand claims database schemas (members, claims, providers, products)
	•	Discover applicable validation rules (data quality + business logic)
	•	Generate SQL queries for claims validation
	•	Automatically identify data quality issues in claims processing

Unlike traditional RAG chatbots, this system focuses on structured data reasoning and actionable outputs (SQL queries), making it highly relevant for healthcare payer operations where claims validation is critical.

⸻

🎯 Problem Statement

**Real-world scenario:** A new QA engineer joins a healthcare payer claims team managing databases with complex claim adjudication logic.

Current challenges:
	•	Claims schemas are complex (7-8 tables) with intricate relationships
	•	Validation rules are scattered across documentation, tribal knowledge, and legacy code
	•	Writing validation SQL is manual, time-consuming, and error-prone
	•	Onboarding takes 2-3 weeks just to understand basic validations

Impact:
	•	Slow onboarding → reduced productivity
	•	Data quality issues → incorrect claim processing
	•	Manual validation → delayed claims adjudication

⸻

💡 Solution

Build an AI-powered assistant that:
	1.	Understands healthcare claims database schema (structure + relationships)
	2.	Retrieves relevant validation rules (data quality + business constraints)
	3.	Generates SQL queries for claims validation
	4.	Routes queries intelligently to the right knowledge base

**Example Interaction:**
- User: *"What validations apply to lab claims?"*
- System: Retrieves 5 relevant rules → Generates SQL for each validation

⸻

🧩 Architecture Overview

🔹 Core Components
User Query
   ↓
Router Agent (Intent Classification)
   ↓
Retriever Layer
   ├── Index 1: Schema Knowledge (Claims DB Structure)
   ├── Index 2: Validation Rules (Data Quality + Business Logic)
   ↓
LLM (OpenAI GPT-4)
   ↓
Response Generator (SQL Queries / Explanations)
   ↓
Streamlit UI

📚 Index Design

📘 Index 1: Schema Knowledge

Represents healthcare payer claims database structure.

**Contains:**
	•	8 tables: claims, claim_lines, members, providers, products, procedure_codes, diagnosis_codes, lab_codes
	•	Column definitions with data types
	•	Relationships (foreign keys)
	•	Business context for each table

**Example:**
```json
{
  "table": "claims",
  "description": "Medical claims submitted by providers for member services",
  "columns": [
    {"name": "claim_id", "type": "VARCHAR(50)", "description": "Unique claim identifier"},
    {"name": "member_id", "type": "VARCHAR(20)", "description": "Member/subscriber ID"},
    {"name": "provider_id", "type": "VARCHAR(15)", "description": "Rendering provider NPI"},
    {"name": "service_date", "type": "DATE", "description": "Date of service"},
    {"name": "claim_status", "type": "VARCHAR(20)", "description": "submitted/approved/denied/pending"}
  ],
  "relationships": [
    "claims.member_id → members.member_id",
    "claims.provider_id → providers.npi",
    "claims.product_id → products.product_id"
  ]
}
```

🧪 Index 2: Validation Rules

Represents claims data quality checks and business constraints.

**Contains:**
	•	20 validation rules (10 data quality + 10 business rules)
	•	Rule metadata (severity, affected tables)
	•	SQL validation query templates
	•	Business context and examples

**Example:**
```json
{
  "rule_id": "CLM_001",
  "rule_name": "Positive Claim Amount",
  "rule_type": "data_quality",
  "tables": ["claims", "claim_lines"],
  "description": "Claim billed amount must be greater than zero",
  "sql_validation": "SELECT claim_id, billed_amount FROM claims WHERE billed_amount <= 0;",
  "severity": "high",
  "business_context": "Zero or negative amounts indicate data entry errors or system issues"
}
```

🤖 Supported Workflows

🟢 1. Schema Understanding

**User Input:** "Explain the claims table structure"

**Uses:** Index 1 (Schema Knowledge)

**Output:** Table description, columns, relationships, business context

⸻

🔵 2. Validation Discovery

**User Input:** "What validations apply to member data?"

**Uses:** Index 2 (Validation Rules)

**Output:** List of relevant rules with descriptions and severity

⸻

🟡 3. SQL Generation (Core Feature)

**User Input:** "Generate SQL to validate claims data quality"

**Uses:** Index 1 + Index 2

**Output:** Multiple SQL validation queries for claims

⸻

🔴 4. Relationship Discovery

**User Input:** "How are claims and providers related?"

**Uses:** Index 1 (Schema Knowledge)

**Output:** Foreign key relationships and join patterns

⸻

🛠 Tech Stack

**MVP (Phase 1 - 2 Weeks)**
	•	**LLM:** OpenAI GPT-4
	•	**Vector DB:** Chroma
	•	**Agent Framework:** LangGraph (router agent)
	•	**Evaluation:** RAGAS (context_precision, answer_relevancy, faithfulness)
	•	**UI:** Streamlit
	•	**Tracing:** LangSmith

**Phase 2 (Post-MVP)**
	•	**Guardrails:** Guardrails AI (SQL validation, safety checks)
	•	**SQL Execution:** Against sample SQLite database
	•	**Enhanced Metrics:** Query correctness, execution results

⸻

📁 Project Structure

```
project/
│
├── data/
│   ├── input/
│   │   ├── claims_schema.json       # 8 tables: claims, claim_lines, members, providers, etc.
│   │   ├── validation_rules.json    # 20 validation rules (10 DQ + 10 business)
│   │   └── sample_claims.sql        # Sample data for testing
│   └── output/
│
├── ingestion/
│   ├── load_schema.py           # Load schema into vector index
│   └── load_rules.py            # Load validation rules into vector index
│
├── retriever/
│   ├── vector_store.py          # Chroma vector store setup
│   └── retrieval.py             # Retrieval logic for both indexes
│
├── agents/
│   ├── router_agent.py          # Intent classification (schema/validation/sql/relationship)
│   └── response_generator.py    # Generate SQL or explanations
│
├── workflows/
│   └── langgraph_flow.py        # LangGraph orchestration
│
├── ui/
│   └── streamlit_app.py         # Streamlit interface
│
├── evaluation/
│   ├── ragas_eval.py            # RAGAS evaluation metrics
│   └── test_queries.json        # 10-15 test queries with expected outputs
│
├── config/
│   └── settings.py              # API keys, model configs
│
├── notebook/
│   └── experiment.ipynb         # Prototyping and testing
│
├── main.py
├── requirements.txt
└── README.md
```

🔄 System Flow

```
1. User Query (Streamlit UI)
      ↓
2. Router Agent (LangGraph)
   - Classify intent: schema | validation | sql_generation | relationship
      ↓
3. Retrieval Layer
   - Query relevant index(es) from Chroma
   - Schema queries → Index 1
   - Validation queries → Index 2
   - SQL generation → Both indexes
      ↓
4. Context + Query → LLM (GPT-4)
      ↓
5. Response Generator
   - SQL queries (validated format)
   - Explanations with business context
      ↓
6. Display in Streamlit UI
   - Show retrieved context
   - Show generated output
   - Display confidence/relevancy scores
```

⸻

🧠 Key Design Decisions

✅ **Scope Choices**
	•	Use 2 indexes only (schema + validation rules) to avoid over-engineering
	•	Focus on healthcare payer claims domain for concrete validation scenarios
	•	20 validation rules: balanced between data quality and business logic

✅ **Technical Choices**
	•	Structured JSON for schema/rules instead of plain text (better retrieval)
	•	LangGraph for agent routing (demonstrates agentic workflows)
	•	Chroma for vector storage (simple, local, no external dependencies)
	•	RAGAS for objective evaluation metrics

✅ **MVP Focus**
	•	Generate SQL, don't execute (execution in Phase 2)
	•	Router agent classification accuracy is key metric
	•	UI shows retrieved context for transparency

✅ **Non-Goals (Out of Scope)**
	•	❌ Not building a full claims adjudication system
	•	❌ Not connecting to real production databases
	•	❌ Not handling schema changes or migrations
	•	✅ Focus: Schema understanding + validation SQL generation

⸻

� 2-Week Development Timeline

**Week 1: Foundation + Data (Days 1-7)**

**Days 1-2** (4-6 hours): Healthcare Claims Schema Design
- Design 8 tables: claims, claim_lines, members, providers, products, procedure_codes, diagnosis_codes, lab_codes
- Document columns, data types, relationships
- Create `claims_schema.json`

**Days 3-4** (4-6 hours): Validation Rules Creation  
- Define 10 data quality rules (nulls, formats, ranges, duplicates)
- Define 10 business rules (timely filing, network validation, medical necessity)
- Create `validation_rules.json`

**Days 5-7** (6-9 hours): Vector Store Setup
- Build ingestion pipeline (`load_schema.py`, `load_rules.py`)
- Create 2 Chroma indexes with appropriate embeddings
- Test retrieval quality (top-k results)

**Week 2: Agent + Evaluation + UI (Days 8-14)**

**Days 8-10** (6-9 hours): Router Agent + Retrieval
- Implement router agent with LangGraph (4 intent classes)
- Build retrieval logic for both indexes
- Test routing accuracy on sample queries

**Days 11-12** (4-6 hours): RAGAS Evaluation
- Create test dataset (10-15 queries with expected outputs)
- Implement RAGAS metrics: context_precision, answer_relevancy, faithfulness
- Measure baseline performance

**Days 13-14** (4-6 hours): Streamlit UI + Demo
- Build Streamlit interface with query input
- Display: user query, router decision, retrieved context, generated output
- Add 4-5 pre-loaded demo queries
- Final testing and documentation

**Total Estimated Hours:** 28-42 hours ✅

⸻

🧪 20 Healthcare Claims Validation Rules

### Data Quality Rules (10)

| Rule ID | Rule Name | Description | Severity |
|---------|-----------|-------------|----------|
| DQ_001 | Positive Claim Amount | Billed amount must be > 0 | High |
| DQ_002 | Service Date Before Submission | Service date < submission date | High |
| DQ_003 | Valid Provider NPI | NPI must be 10 digits | High |
| DQ_004 | No Duplicate Claims | Same member+provider+service date+amount | Medium |
| DQ_005 | Valid Procedure Codes | CPT/HCPCS codes exist in reference table | High |
| DQ_006 | Valid Diagnosis Codes | ICD-10 codes properly formatted | High |
| DQ_007 | Valid Claim Status | Status in (submitted, approved, denied, pending) | Medium |
| DQ_008 | Valid Lab Codes | Lab codes exist in LOINC reference | Medium |
| DQ_009 | Billed vs Paid Amount Logic | Paid <= Billed amount | High |
| DQ_010 | Required Fields Check | Claim_id, member_id, provider_id not null | High |

### Business Rules (10)

| Rule ID | Rule Name | Description | Severity |
|---------|-----------|-------------|----------|
| BR_001 | Active Member Coverage | Member active on service date | Critical |
| BR_002 | In-Network Provider | Provider in network for member's product | High |
| BR_003 | Timely Filing Limit | Claim filed within 90 days of service | High |
| BR_004 | Prior Authorization Required | Specific procedures need pre-auth | High |
| BR_005 | Age-Appropriate Services | Procedure valid for member age group | Medium |
| BR_006 | Gender-Specific Procedures | Procedure matches member gender | Medium |
| BR_007 | Diagnosis-Procedure Match | Procedure clinically appropriate for diagnosis | Medium |
| BR_008 | Benefit Limit Check | Service count within plan limits | High |
| BR_009 | Coordination of Benefits | Primary vs secondary payer logic | Medium |
| BR_010 | Place of Service Validation | Procedure allowed at service location code | Medium |

⸻

📊 RAGAS Evaluation Metrics

**Metrics to Measure (MVP)**
1. **Context Precision**: Are the retrieved schema/rules relevant to the query?
2. **Answer Relevancy**: Does the generated SQL/explanation address the query?
3. **Faithfulness**: Is the output grounded in the retrieved context?

**Success Criteria**
- Context Precision: ≥ 0.75 (75% of retrieved docs are relevant)
- Answer Relevancy: ≥ 0.80 (80% relevance to query)
- Faithfulness: ≥ 0.85 (85% grounded in context, no hallucinations)

**Test Dataset**: 10-15 queries covering all 4 workflow types

⸻

🚀 How to Run

### Setup
```bash
# Clone repo
git clone <repo-url>
cd AGENTIC_RAG

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your_openai_key
export LANGCHAIN_API_KEY=your_langsmith_key  # Optional for tracing
```

### Load Data into Vector Store
```bash
# Load schema and validation rules into Chroma
python ingestion/load_schema.py
python ingestion/load_rules.py
```

### Run Application
```bash
# Start Streamlit UI
streamlit run ui/streamlit_app.py

# Or run via main entry point
python main.py
```

### Run Evaluation
```bash
# Evaluate with RAGAS
python evaluation/ragas_eval.py
```

⸻

🎓 Learning Outcomes Demonstrated

This capstone project demonstrates mastery of:

✅ **Retrieval-Augmented Generation (RAG)**
- Multi-index architecture with domain-specific knowledge bases
- Semantic search and context retrieval optimization
- Structured data representation in vector stores

✅ **Agentic Workflows with LangGraph**
- Intent classification with router agents
- Multi-step reasoning and tool selection
- State management across agent interactions

✅ **Prompt Engineering**
- Context-aware prompt templates for SQL generation
- Few-shot learning for validation rule explanation
- Chain-of-thought reasoning for complex queries

✅ **Evaluation & Metrics**
- RAGAS framework implementation (context precision, faithfulness, relevancy)
- Test dataset creation with ground truth
- Performance benchmarking and iteration

✅ **Production Considerations**
- Structured logging and tracing (LangSmith)
- Error handling for malformed queries
- Token optimization strategies
- User interface design for transparency

⸻

🔮 Phase 2 Roadmap (Post-MVP)

Once MVP is complete, consider these enhancements:

1. **SQL Execution Engine**
   - Create sample SQLite database with synthetic claims data
   - Execute generated SQL and display results
   - Show validation failures with row counts

2. **Guardrails AI Integration**
   - Validate generated SQL syntax before display
   - Prevent SQL injection patterns
   - Check for performance concerns (missing WHERE clauses, etc.)

3. **Enhanced Retrieval**
   - Hybrid search (semantic + keyword)
   - Re-ranking with cross-encoder models
   - Query expansion and synonym handling

4. **Advanced UI Features**
   - Query history and favorites
   - Export SQL to file
   - Side-by-side comparison of multiple validation approaches
   - Visualization of schema relationships

⸻

📚 References & Resources

- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **RAGAS Framework**: https://docs.ragas.io/
- **Chroma Vector DB**: https://docs.trychroma.com/
- **Healthcare Claims Standards**: 
  - CPT Codes: https://www.ama-assn.org/practice-management/cpt
  - ICD-10: https://www.cdc.gov/nchs/icd/icd-10-cm.htm
  - LOINC Lab Codes: https://loinc.org/

⸻

🤝 Contributing

This is a capstone project for educational purposes. Feedback and suggestions are welcome!

⸻

📄 License

MIT License - feel free to use this as a template for your own projects.