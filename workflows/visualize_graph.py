"""
Visualize the LangGraph workflow with clean, visible styling.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflows.graph_builder import create_workflow


def visualize_workflow(format="mermaid"):
    """
    Generate workflow visualization.
    
    Args:
        format: "mermaid" or "info"
    
    Returns:
        dict: Contains mermaid_code or graph info
    """
    workflow = create_workflow()
    app = workflow.compile()
    graph = app.get_graph()
    
    result = {}
    
    if format == "mermaid":
        # Get base mermaid code from LangGraph
        mermaid_code = graph.draw_mermaid()
        
        # Remove the :::first and :::last classes that apply different styling
        mermaid_code = mermaid_code.replace(":::first", "")
        mermaid_code = mermaid_code.replace(":::last", "")
        
        # Uniform color scheme with proper node background colors:
        # - All nodes: Light blue background (#e3f2fd) with dark blue text/border (#1565c0)
        # - All edges: Black (#000000)
        config = """%%{init: {'theme':'base', 'themeVariables': {
            'primaryColor':'#e3f2fd',
            'primaryTextColor':'#1565c0',
            'primaryBorderColor':'#1565c0',
            'lineColor':'#000000',
            'secondaryColor':'#e3f2fd',
            'tertiaryColor':'#e3f2fd',
            'clusterBkg':'#e3f2fd',
            'clusterBorder':'#1565c0',
            'defaultLinkColor':'#000000',
            'edgeLabelBackground':'#ffffff',
            'nodeTextColor':'#1565c0'
        }}}%%"""
        
        # Replace the config section
        if "---\nconfig:" in mermaid_code:
            graph_start = mermaid_code.find("graph TD;")
            if graph_start != -1:
                mermaid_code = config + "\n" + mermaid_code[graph_start:]
        
        result['mermaid'] = mermaid_code
    
    elif format == "info":
        result['info'] = {
            'nodes': [str(node) for node in graph.nodes],
            'edges': [f"{edge.source} → {edge.target}" for edge in graph.edges],
            'description': "RAG workflow: Router → Retriever → Generator"
        }
    
    return result


if __name__ == "__main__":
    print("\n🎨 VISUALIZING LANGGRAPH WORKFLOW\n")
    
    # Get workflow info
    info_viz = visualize_workflow(format="info")
    
    print("="*80)
    print("WORKFLOW STRUCTURE")
    print("="*80 + "\n")
    
    print("📊 Nodes:")
    for node in info_viz['info']['nodes']:
        print(f"  • {node}")
    
    print("\n🔗 Edges:")
    for edge in info_viz['info']['edges']:
        print(f"  • {edge}")
    
    print("\n📝 Description:")
    print(info_viz['info']['description'])
    
    # Get Mermaid diagram
    mermaid_viz = visualize_workflow(format="mermaid")
    
    print("\n" + "="*80)
    print("MERMAID DIAGRAM CODE")
    print("="*80 + "\n")
    print(mermaid_viz['mermaid'])
    
    print("\n" + "="*80)
    print("✅ VISUALIZATION COMPLETE")
    print("="*80)
    print("\n💡 The Mermaid diagram can be:")
    print("  • Rendered visually in compatible tools")
    print("  • Pasted into GitHub README.md")
    print("  • Used in any Mermaid-compatible viewer")
    print()
