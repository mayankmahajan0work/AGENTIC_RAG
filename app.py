"""
Streamlit UI for RAG Assistant

Interface with expandable sections for details.
"""

import streamlit as st
import streamlit.components.v1 as components
from main import run_query
from config.settings import validate_settings
from workflows.visualize_graph import visualize_workflow

# Validate configuration on startup
validate_settings()

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
    .stButton button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🏥 AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Ask questions about database schema, validation rules, or get SQL queries (Demo: Healthcare Claims)</div>', unsafe_allow_html=True)

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
                # Note: st.code has a built-in copy button in Streamlit 1.29+
    
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
    - 📊 Explore database schema & relationships
    - ✅ Check validation rules
    - 💻 Generate SQL queries
    
    **Intent Types:**
    - `schema`: Table structures and relationships
    - `validation`: Data quality rules
    - `sql`: SQL query generation
    """)
    
    st.markdown("---")
    st.markdown("### 📈 System Info")
    st.markdown(f"""
    - **Vector Store:** ChromaDB
    - **LLM:** GPT-4o-mini
    - **Collections:** 2
    - **Documents:** 28
    """)
    
    st.markdown("---")
    
    # Workflow visualization section
    st.markdown("### 🔄 Workflow")
    show_workflow = st.session_state.get("show_workflow", False)
    button_label = "🙈 Hide LangGraph Flow" if show_workflow else "📊 Show LangGraph Flow"
    
    if st.button(button_label, use_container_width=True):
        st.session_state.show_workflow = not show_workflow
        st.rerun()
    
    # Display workflow diagram if toggled
    if st.session_state.get("show_workflow", False):
        with st.spinner("Generating workflow diagram..."):
            try:
                viz = visualize_workflow(format="mermaid")
                mermaid_code = viz.get("mermaid", "")
                
                # Render mermaid diagram using HTML component with light background
                mermaid_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{
                            background-color: #ffffff;
                            padding: 20px;
                            margin: 0;
                        }}
                        .mermaid {{
                            background-color: #ffffff;
                        }}
                    </style>
                </head>
                <body>
                    <div class="mermaid">
                    {mermaid_code}
                    </div>
                    <script type="module">
                      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                      mermaid.initialize({{ startOnLoad: true }});
                    </script>
                </body>
                </html>
                """
                components.html(mermaid_html, height=400, scrolling=True)
                
            except Exception as e:
                st.error(f"Error generating diagram: {e}")
                st.info("The workflow has 3 stages: Router → Retriever → Generator")

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.875rem;">Built with Streamlit • Powered by LangGraph & ChromaDB</div>',
    unsafe_allow_html=True
)
