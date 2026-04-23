"""
Streamlit UI for RAG Assistant

Interface with expandable sections for details.
"""

import streamlit as st
from main import run_query

# Page config
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for cleaner look
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .intent-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    .intent-schema { background-color: #e3f2fd; color: #1565c0; }
    .intent-validation { background-color: #fff3e0; color: #e65100; }
    .intent-sql { background-color: #e8f5e9; color: #2e7d32; }
    .intent-relationship { background-color: #f3e5f5; color: #6a1b9a; }
    .stButton button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🏥 AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Ask questions about claims data, schema, validation rules, or get SQL queries</div>', unsafe_allow_html=True)

# Example queries
st.markdown("**💡 Try these examples:**")
col1, col2, col3 = st.columns(3)

example_queries = {
    "Schema": "What columns are in the claims table?",
    "Validation": "What are the data quality rules for claims?",
    "SQL": "Find all claims over $5000"
}

with col1:
    if st.button("📊 Schema Query", use_container_width=True):
        st.session_state.example_query = example_queries["Schema"]

with col2:
    if st.button("✅ Validation Query", use_container_width=True):
        st.session_state.example_query = example_queries["Validation"]

with col3:
    if st.button("💻 SQL Query", use_container_width=True):
        st.session_state.example_query = example_queries["SQL"]

st.markdown("---")

# Query input
query = st.text_area(
    "💬 Ask a question:",
    value=st.session_state.get("example_query", ""),
    placeholder="e.g., What columns are in the claims table? or Find all claims with billed_amount > 5000",
    height=100,
    key="query_input"
)

# Clear example query after it's been used
if "example_query" in st.session_state:
    del st.session_state.example_query

# Ask button
ask_button = st.button("🚀 Ask", type="primary", use_container_width=True)

# Process query
if ask_button and query.strip():
    with st.spinner("🔍 Processing your question..."):
        try:
            # Run query through RAG pipeline
            result = run_query(query)
            
            # Store in session state
            st.session_state.last_result = result
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.session_state.last_result = None

# Display results
if "last_result" in st.session_state and st.session_state.last_result:
    result = st.session_state.last_result
    
    st.markdown("---")
    
    # Intent badge
    intent = result.get("intent", "unknown")
    intent_class = f"intent-{intent}"
    st.markdown(f'<div class="intent-badge {intent_class}">🎯 Intent: {intent}</div>', unsafe_allow_html=True)
    
    # Sources summary
    sources = result.get("metadata", {}).get("sources", [])
    num_docs = result.get("num_docs_retrieved", 0)
    if sources:
        st.caption(f"📚 {len(sources)} sources used | {num_docs} documents retrieved")
    
    # Response section (always visible)
    st.markdown("### 💡 Answer")
    response = result.get("response", "No response generated")
    
    # Remove source attribution from response if present (we'll show it in expander)
    if "---\n📚 **Sources Used:**" in response:
        response = response.split("---\n📚 **Sources Used:**")[0].strip()
    
    st.markdown(response)
    
    # Expandable sections
    st.markdown("")
    
    # SQL Query section (if applicable)
    sql_queries = result.get("sql_queries", [])
    if sql_queries:
        with st.expander("📊 Show SQL Query", expanded=False):
            for i, sql in enumerate(sql_queries, 1):
                if len(sql_queries) > 1:
                    st.markdown(f"**Query {i}:**")
                st.code(sql, language="sql")
                if st.button(f"📋 Copy SQL {i if len(sql_queries) > 1 else ''}", key=f"copy_{i}"):
                    st.toast("✅ SQL copied to clipboard!")
    
    # Retrieved Context section
    contexts = result.get("retrieved_context", [])
    if contexts:
        with st.expander(f"📖 Show Retrieved Context ({len(contexts)} documents)", expanded=False):
            for i, doc in enumerate(contexts, 1):
                st.markdown(f"**Document {i}:**")
                st.text(doc.page_content if hasattr(doc, 'page_content') else str(doc))
                st.markdown("---")
    
    # Sources section
    if sources:
        with st.expander(f"📚 Show Sources ({len(sources)} items)", expanded=False):
            # Group sources by type
            tables = [s for s in sources if s.startswith("Table:")]
            rules = [s for s in sources if s.startswith("Rule:")]
            
            if tables:
                st.markdown("**📊 Tables:**")
                for table in tables:
                    st.markdown(f"- {table}")
            
            if rules:
                st.markdown("**✅ Validation Rules:**")
                for rule in rules:
                    st.markdown(f"- {rule}")

# Sidebar with info
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.markdown("""
    This RAG system helps you:
    - 📊 Explore database schema
    - ✅ Check validation rules
    - 💻 Generate SQL queries
    - 🔗 Understand relationships
    
    **Intent Types:**
    - `schema`: Table structures
    - `validation`: Data quality rules
    - `sql`: SQL query generation
    - `relationship`: Table relationships
    """)
    
    st.markdown("---")
    st.markdown("### 📈 System Info")
    st.markdown(f"""
    - **Vector Store:** ChromaDB
    - **LLM:** GPT-4o-mini
    - **Collections:** 2
    - **Documents:** 28
    """)

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.875rem;">Built with Streamlit • Powered by LangGraph & ChromaDB</div>',
    unsafe_allow_html=True
)
