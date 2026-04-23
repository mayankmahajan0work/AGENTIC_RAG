"""
Visualize the LangGraph workflow.

Generates Mermaid diagrams and ASCII representations of the workflow graph.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflows.graph_builder import create_workflow


def visualize_workflow(format="all"):
    """
    Visualize the LangGraph workflow in various formats.
    
    Args:
        format: "all", "mermaid", "ascii", or "info"
    
    Returns:
        dict: Contains mermaid_code, ascii_diagram, and graph info
    """
    # Create workflow once (avoid duplication)
    workflow = create_workflow()
    app = workflow.compile()
    graph = app.get_graph()
    
    result = {}
    
    # Mermaid diagram
    if format in ["all", "mermaid"]:
        result['mermaid'] = graph.draw_mermaid()
    
    # ASCII diagram
    if format in ["all", "ascii"]:
        try:
            result['ascii'] = graph.draw_ascii()
        except Exception as e:
            result['ascii'] = f"ASCII diagram not available: {e}"
    
    # Graph info
    if format in ["all", "info"]:
        nodes = [str(node) for node in graph.nodes]
        edges = [f"{edge.source} → {edge.target}" for edge in graph.edges]
        result['info'] = {
            'nodes': nodes,
            'edges': edges,
            'description': (
                "RAG workflow with 3 stages:\n"
                "  1. Router: Classifies user intent\n"
                "  2. Retriever: Fetches relevant context from ChromaDB\n"
                "  3. Generator: Creates SQL queries or explanations using LLM"
            )
        }
    
    return result


if __name__ == "__main__":
    print("\n🎨 VISUALIZING LANGGRAPH WORKFLOW\n")
    
    # Get all visualization formats
    viz = visualize_workflow(format="all")
    
    # Print graph information
    print("="*80)
    print("WORKFLOW STRUCTURE")
    print("="*80 + "\n")
    
    print("📊 Nodes:")
    for node in viz['info']['nodes']:
        print(f"  • {node}")
    
    print("\n🔗 Edges:")
    for edge in viz['info']['edges']:
        print(f"  • {edge}")
    
    print("\n📝 Description:")
    print(viz['info']['description'])
    
    # Print ASCII diagram
    print("\n" + "="*80)
    print("ASCII DIAGRAM")
    print("="*80 + "\n")
    print(viz['ascii'])
    
    # Print Mermaid diagram
    print("\n" + "="*80)
    print("MERMAID DIAGRAM CODE")
    print("="*80 + "\n")
    print(viz['mermaid'])
    
    print("\n" + "="*80)
    print("✅ VISUALIZATION COMPLETE")
    print("="*80)
    print("\n💡 The Mermaid diagram can be:")
    print("  • Rendered visually in compatible tools")
    print("  • Pasted into GitHub README.md")
    print("  • Used in any Mermaid-compatible viewer")
    print()
