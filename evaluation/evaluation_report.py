"""
Generate evaluation reports from RAGAS results.

Creates formatted reports showing:
- Overall scores and benchmarks
- Performance by intent type
- Detailed breakdown of metrics
- Historical comparison (if available)
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


# Quality benchmarks
BENCHMARKS = {
    'context_precision': {
        'excellent': 0.85,
        'good': 0.75,
        'fair': 0.65,
        'description': 'Measures if retrieved documents are relevant to the question'
    },
    'answer_relevancy': {
        'excellent': 0.85,
        'good': 0.75,
        'fair': 0.65,
        'description': 'Measures if the answer addresses the question'
    },
    'faithfulness': {
        'excellent': 0.90,
        'good': 0.80,
        'fair': 0.70,
        'description': 'Measures if answer is grounded in context (no hallucination)'
    }
}


def get_quality_rating(metric_name: str, score: float) -> str:
    """
    Get quality rating for a metric score.
    
    Args:
        metric_name: Name of the metric
        score: Metric score (0-1)
    
    Returns:
        Quality rating string
    """
    if metric_name not in BENCHMARKS:
        return "Unknown"
    
    benchmarks = BENCHMARKS[metric_name]
    
    if score >= benchmarks['excellent']:
        return "Excellent ✅"
    elif score >= benchmarks['good']:
        return "Good ✓"
    elif score >= benchmarks['fair']:
        return "Fair ⚠️"
    else:
        return "Needs Improvement ❌"


def generate_report(results: Dict[str, Any], output_dir: str = "evaluation/reports") -> str:
    """
    Generate a formatted evaluation report.
    
    Args:
        results: Evaluation results dictionary
        output_dir: Directory to save the report
    
    Returns:
        Path to the generated report
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_path / f"evaluation_report_{timestamp}.md"
    
    # Build report content
    report_lines = []
    
    # Header
    report_lines.append("# RAG System Evaluation Report")
    report_lines.append("")
    report_lines.append(f"**Generated:** {results.get('timestamp', 'N/A')}")
    report_lines.append(f"**Test Queries:** {results.get('num_successful', 0)}/{results.get('num_queries', 0)} successful")
    report_lines.append("")
    
    # Overall Scores
    report_lines.append("## Overall Performance")
    report_lines.append("")
    report_lines.append("| Metric | Score | Rating | Benchmark |")
    report_lines.append("|--------|-------|--------|-----------|")
    
    metrics = results.get('metrics', {})
    for metric_name, score in metrics.items():
        rating = get_quality_rating(metric_name, score)
        benchmark_info = BENCHMARKS.get(metric_name, {})
        excellent = benchmark_info.get('excellent', 0.85)
        report_lines.append(f"| {metric_name} | {score:.3f} | {rating} | ≥{excellent:.2f} |")
    
    report_lines.append("")
    
    # Metric Descriptions
    report_lines.append("## Metric Descriptions")
    report_lines.append("")
    for metric_name, score in metrics.items():
        if metric_name in BENCHMARKS:
            desc = BENCHMARKS[metric_name]['description']
            report_lines.append(f"**{metric_name}**: {desc}")
            report_lines.append("")
    
    # Quality Assessment
    report_lines.append("## Quality Assessment")
    report_lines.append("")
    
    avg_score = sum(metrics.values()) / len(metrics) if metrics else 0
    
    if avg_score >= 0.85:
        assessment = "✅ **Excellent** - System is production-ready with high quality responses"
    elif avg_score >= 0.75:
        assessment = "✓ **Good** - System performs well, minor improvements possible"
    elif avg_score >= 0.65:
        assessment = "⚠️ **Fair** - System needs improvement before production"
    else:
        assessment = "❌ **Needs Improvement** - Significant issues need to be addressed"
    
    report_lines.append(f"**Overall Score:** {avg_score:.3f}")
    report_lines.append("")
    report_lines.append(assessment)
    report_lines.append("")
    
    # Recommendations
    report_lines.append("## Recommendations")
    report_lines.append("")
    
    recommendations = []
    
    context_prec = metrics.get('context_precision', 1.0)
    answer_rel = metrics.get('answer_relevancy', 1.0)
    faith = metrics.get('faithfulness', 1.0)
    
    if context_prec < 0.75:
        recommendations.append("- **Improve Retrieval**: Context precision is low. Consider:")
        recommendations.append("  - Tuning embedding model")
        recommendations.append("  - Increasing number of retrieved documents")
        recommendations.append("  - Improving document chunking strategy")
    
    if answer_rel < 0.75:
        recommendations.append("- **Improve Answer Quality**: Answer relevancy is low. Consider:")
        recommendations.append("  - Refining LLM prompts")
        recommendations.append("  - Adding more examples to prompts")
        recommendations.append("  - Using different LLM temperature")
    
    if faith < 0.80:
        recommendations.append("- **Reduce Hallucination**: Faithfulness is low. Consider:")
        recommendations.append("  - Strengthening prompt instructions")
        recommendations.append("  - Adding validation guardrails")
        recommendations.append("  - Using lower temperature (more deterministic)")
    
    if not recommendations:
        recommendations.append("- No major issues detected. Consider:")
        recommendations.append("  - Expanding test coverage")
        recommendations.append("  - Testing edge cases")
        recommendations.append("  - Monitoring production performance")
    
    report_lines.extend(recommendations)
    report_lines.append("")
    
    # Benchmarks Reference
    report_lines.append("## Quality Benchmarks")
    report_lines.append("")
    report_lines.append("| Rating | Threshold |")
    report_lines.append("|--------|-----------|")
    report_lines.append("| Excellent ✅ | ≥0.85 |")
    report_lines.append("| Good ✓ | ≥0.75 |")
    report_lines.append("| Fair ⚠️ | ≥0.65 |")
    report_lines.append("| Needs Improvement ❌ | <0.65 |")
    report_lines.append("")
    
    # Footer
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("*Generated by RAGAS Evaluation Module*")
    
    # Write report
    report_content = "\n".join(report_lines)
    report_file.write_text(report_content)
    
    # Also save JSON version
    json_file = output_path / f"evaluation_results_{timestamp}.json"
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    return str(report_file)


def print_summary(results: Dict[str, Any]) -> None:
    """
    Print a concise summary of evaluation results to console.
    
    Args:
        results: Evaluation results dictionary
    """
    print(f"\n{'='*80}")
    print(f"EVALUATION SUMMARY")
    print(f"{'='*80}\n")
    
    if 'error' in results:
        print(f"❌ Evaluation failed: {results['error']}")
        return
    
    # Basic info
    print(f"Queries: {results.get('num_successful', 0)}/{results.get('num_queries', 0)} successful")
    print(f"Timestamp: {results.get('timestamp', 'N/A')}\n")
    
    # Metrics
    print("Scores:")
    metrics = results.get('metrics', {})
    for metric_name, score in metrics.items():
        rating = get_quality_rating(metric_name, score)
        print(f"  {metric_name:20s}: {score:.3f} - {rating}")
    
    # Overall
    if metrics:
        avg_score = sum(metrics.values()) / len(metrics)
        print(f"\n  {'Average':20s}: {avg_score:.3f}")
    
    print(f"\n{'='*80}\n")


def compare_results(current: Dict[str, Any], previous: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare current results with previous evaluation.
    
    Args:
        current: Current evaluation results
        previous: Previous evaluation results
    
    Returns:
        Comparison dictionary with changes
    """
    comparison = {
        'timestamp': datetime.now().isoformat(),
        'current_date': current.get('timestamp'),
        'previous_date': previous.get('timestamp'),
        'changes': {}
    }
    
    current_metrics = current.get('metrics', {})
    previous_metrics = previous.get('metrics', {})
    
    for metric_name in current_metrics:
        if metric_name in previous_metrics:
            current_score = current_metrics[metric_name]
            previous_score = previous_metrics[metric_name]
            change = current_score - previous_score
            
            comparison['changes'][metric_name] = {
                'current': current_score,
                'previous': previous_score,
                'change': change,
                'improved': change > 0
            }
    
    return comparison


if __name__ == "__main__":
    # Example usage
    example_results = {
        'timestamp': datetime.now().isoformat(),
        'num_queries': 20,
        'num_successful': 18,
        'metrics': {
            'context_precision': 0.82,
            'answer_relevancy': 0.88,
            'faithfulness': 0.85
        }
    }
    
    print("Generating example report...")
    report_path = generate_report(example_results)
    print(f"✅ Report saved to: {report_path}")
    
    print_summary(example_results)
