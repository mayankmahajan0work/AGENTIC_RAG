"""
Main entry point for the Agentic RAG system.

Run queries through the RAG pipeline:
- User Query → Router → Vector Store(s) → Response Generator → Output
"""

from typing import Dict, Any

from workflows.graph_builder import create_workflow


def run_query(query: str) -> Dict[str, Any]:
    """
    Run a query through the complete RAG pipeline.
    
    This is the main entry point for processing user queries.
    
    Args:
        query: User's question
    
    Returns:
        Dictionary with response and metadata
    """
    # Initialize state
    initial_state = {
        "query": query,
        "intent": None,
        "retrieved_context": [],
        "response": "",
        "sql_queries": [],
        "metadata": {}
    }
    
    # Create and compile workflow
    workflow = create_workflow()
    app = workflow.compile()
    
    # Run workflow
    print(f"\n{'='*80}")
    print(f"🚀 Processing Query: {query}")
    print(f"{'='*80}\n")
    
    final_state = app.invoke(initial_state)
    
    print(f"\n{'='*80}")
    print(f"✅ Query Processing Complete")
    print(f"{'='*80}\n")
    
    # Return useful info
    return {
        "query": final_state["query"],
        "intent": final_state["intent"],
        "response": final_state["response"],
        "sql_queries": final_state["sql_queries"],
        "num_docs_retrieved": len(final_state["retrieved_context"]),
        "retrieved_context": final_state["retrieved_context"],  # Include for evaluation
        "metadata": final_state["metadata"]
    }


def run_query_streaming(query: str):
    """
    Run query with streaming output (for real-time feedback).
    
    Yields state updates as the workflow progresses.
    
    Args:
        query: User's question
    
    Yields:
        State updates from each node
    """
    # Initialize state
    initial_state = {
        "query": query,
        "intent": None,
        "retrieved_context": [],
        "response": "",
        "sql_queries": [],
        "metadata": {}
    }
    
    # Create and compile workflow
    workflow = create_workflow()
    app = workflow.compile()
    
    # Stream results
    for state_update in app.stream(initial_state):
        yield state_update


def main():
    """
    Interactive mode - run queries from command line.
    """
    print("\n" + "="*80)
    print("🤖 AGENTIC RAG FOR HEALTHCARE CLAIMS DATA VALIDATION")
    print("="*80)
    print("\nAsk questions about:")
    print("  • Table schemas and structures")
    print("  • Data validation rules")
    print("  • SQL query generation")
    print("  • Table relationships")
    print("\nType 'exit' to quit\n")
    
    while True:
        query = input("🔍 Your question: ").strip()
        
        if query.lower() in ['exit', 'quit', 'q']:
            print("\n👋 Goodbye!\n")
            break
        
        if not query:
            continue
        
        # Run query
        result = run_query(query)
        
        # Display response
        print("\n" + "="*80)
        print("📝 RESPONSE:")
        print("="*80)
        print(result['response'])
        print("="*80 + "\n")


if __name__ == "__main__":
    main()
