"""
Visualize the LangGraph workflow using Mermaid diagrams.

Automatically generates and renders the graph structure.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflows.graph_builder import create_workflow


def get_mermaid_diagram():
    """
    Generate Mermaid diagram code from the LangGraph workflow.
    
    Returns:
        str: Mermaid diagram markup
    """
    # Create and compile the workflow
    workflow = create_workflow()
    app = workflow.compile()
    
    # Get the graph and generate Mermaid diagram
    graph = app.get_graph()
    mermaid_code = graph.draw_mermaid()
    
    return mermaid_code


def print_ascii_diagram():
    """
    Print ASCII representation of the graph.
    """
    workflow = create_workflow()
    app = workflow.compile()
    graph = app.get_graph()
    
    try:
        ascii_diagram = graph.draw_ascii()
        return ascii_diagram
    except Exception as e:
        return f"ASCII diagram not available: {e}"


def print_graph_info():
    """
    Print information about the graph structure.
    """
    workflow = create_workflow()
    app = workflow.compile()
    graph = app.get_graph()
    
    print("\n" + "="*80)
    print("LANGGRAPH WORKFLOW STRUCTURE")
    print("="*80 + "\n")
    
    print("📊 Nodes:")
    for node in graph.nodes:
        print(f"  • {node}")
    
    print("\n🔗 Edges:")
    for edge in graph.edges:
        print(f"  • {edge.source} → {edge.target}")
    
    print("\n📝 Workflow Description:")
    print("  This is a linear pipeline with 3 processing nodes:")
    print("  1. Router: Classifies user intent")
    print("  2. Retriever: Fetches relevant context from ChromaDB")
    print("  3. Generator: Creates SQL queries or explanations using LLM")


if __name__ == "__main__":
    print("\n🎨 VISUALIZING LANGGRAPH WORKFLOW\n")
    
    # Print graph information
    print_graph_info()
    
    # Print ASCII diagram
    print("\n" + "="*80)
    print("ASCII DIAGRAM")
    print("="*80 + "\n")
    ascii_diagram = print_ascii_diagram()
    print(ascii_diagram)
    
    # Get Mermaid diagram
    print("\n" + "="*80)
    print("MERMAID DIAGRAM CODE")
    print("="*80 + "\n")
    mermaid_code = get_mermaid_diagram()
    print(mermaid_code)
    
    print("\n" + "="*80)
    print("✅ VISUALIZATION COMPLETE")
    print("="*80)
    print("\n💡 The Mermaid diagram above can be:")
    print("  • Rendered visually (see below)")
    print("  • Pasted into GitHub README.md")
    print("  • Used in any Mermaid-compatible tool")
    print()
