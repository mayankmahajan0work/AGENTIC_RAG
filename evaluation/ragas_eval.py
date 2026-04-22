"""
RAGAS-based evaluation of RAG system quality.

Evaluates the system using three key metrics:
1. Context Precision: Are retrieved documents relevant to the question?
2. Answer Relevancy: Does the answer address the question?
3. Faithfulness: Is the answer grounded in retrieved context (no hallucination)?
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_precision
)
from datasets import Dataset

from main import run_query
from evaluation.test_queries import TEST_QUERIES, get_test_queries_by_type


def collect_evaluation_data(test_queries: List[Dict[str, Any]], verbose: bool = True) -> Dict[str, List]:
    """
    Run test queries through the system and collect data for RAGAS evaluation.
    
    Args:
        test_queries: List of test query dictionaries
        verbose: Whether to print progress
    
    Returns:
        Dictionary with lists of questions, contexts, answers, and ground_truths
    """
    questions = []
    contexts = []
    answers = []
    ground_truths = []
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"COLLECTING DATA FROM {len(test_queries)} TEST QUERIES")
        print(f"{'='*80}\n")
    
    for i, test_query in enumerate(test_queries, 1):
        question = test_query['question']
        ground_truth = test_query['ground_truth']
        
        if verbose:
            print(f"[{i}/{len(test_queries)}] Processing: {question[:60]}...")
        
        try:
            # Run query through the system
            result = run_query(question)
            
            # Extract data
            answer = result['response']
            
            # Extract contexts from retrieved documents
            retrieved_docs = result.get('retrieved_context', [])
            context_list = [doc['content'] for doc in retrieved_docs]
            
            # RAGAS expects a list of context strings
            questions.append(question)
            contexts.append(context_list)  # List of strings
            answers.append(answer)
            ground_truths.append(ground_truth)
            
            if verbose:
                print(f"   ✅ Retrieved {len(context_list)} contexts, generated answer ({len(answer)} chars)")
        
        except Exception as e:
            if verbose:
                print(f"   ❌ Error: {str(e)}")
            # Skip failed queries
            continue
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"COLLECTION COMPLETE: {len(questions)} queries processed successfully")
        print(f"{'='*80}\n")
    
    return {
        'question': questions,
        'contexts': contexts,
        'answer': answers,
        'ground_truth': ground_truths
    }


def evaluate_system(
    test_queries: List[Dict[str, Any]] = None,
    metrics: List = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Evaluate the RAG system using RAGAS metrics.
    
    Args:
        test_queries: List of test queries to evaluate (defaults to all TEST_QUERIES)
        metrics: List of RAGAS metrics to use (defaults to all three)
        verbose: Whether to print progress
    
    Returns:
        Dictionary with evaluation results and scores
    """
    # Default to all test queries
    if test_queries is None:
        test_queries = TEST_QUERIES
    
    # Default metrics
    if metrics is None:
        metrics = [
            context_precision,
            answer_relevancy,
            faithfulness
        ]
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"RAGAS EVALUATION")
        print(f"{'='*80}")
        print(f"\nMetrics to evaluate:")
        for metric in metrics:
            print(f"  - {metric.name}")
        print()
    
    # Collect data
    eval_data = collect_evaluation_data(test_queries, verbose=verbose)
    
    # Create dataset
    dataset = Dataset.from_dict(eval_data)
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"RUNNING RAGAS EVALUATION")
        print(f"{'='*80}\n")
        print("This may take a few minutes...\n")
    
    # Run evaluation
    try:
        results = evaluate(dataset, metrics=metrics)
        
        if verbose:
            print(f"\n{'='*80}")
            print(f"EVALUATION COMPLETE")
            print(f"{'='*80}\n")
    
    except Exception as e:
        print(f"\n❌ Evaluation failed: {str(e)}")
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
    
    # Package results
    evaluation_results = {
        'timestamp': datetime.now().isoformat(),
        'num_queries': len(test_queries),
        'num_successful': len(eval_data['question']),
        'metrics': {},
        'raw_results': str(results)  # Convert to string for JSON serialization
    }
    
    # Extract metric scores from RAGAS results
    # RAGAS returns a dict-like object with metric names as keys
    results_dict = results.to_pandas().to_dict()
    
    for metric in metrics:
        metric_name = metric.name
        # Get the mean score across all samples
        if metric_name in results_dict:
            scores = list(results_dict[metric_name].values())
            if scores:
                evaluation_results['metrics'][metric_name] = sum(scores) / len(scores)
    
    return evaluation_results


def run_full_evaluation(save_report: bool = True) -> Dict[str, Any]:
    """
    Run complete evaluation on all test queries.
    
    Args:
        save_report: Whether to save results to file
    
    Returns:
        Evaluation results dictionary
    """
    print(f"\n{'='*80}")
    print(f"FULL SYSTEM EVALUATION")
    print(f"{'='*80}\n")
    
    # Run evaluation
    results = evaluate_system(
        test_queries=TEST_QUERIES,
        verbose=True
    )
    
    # Print summary
    if 'error' not in results:
        print(f"\n{'='*80}")
        print(f"RESULTS SUMMARY")
        print(f"{'='*80}\n")
        
        print(f"Queries evaluated: {results['num_successful']}/{results['num_queries']}")
        print(f"\nMetric Scores:")
        
        for metric_name, score in results['metrics'].items():
            # Format score with color coding
            if score >= 0.85:
                status = "✅ Excellent"
            elif score >= 0.75:
                status = "✓ Good"
            elif score >= 0.65:
                status = "⚠ Fair"
            else:
                status = "❌ Needs Improvement"
            
            print(f"  {metric_name:20s}: {score:.3f} {status}")
        
        # Save report if requested
        if save_report:
            from evaluation.evaluation_report import generate_report
            report_path = generate_report(results)
            print(f"\n📄 Report saved to: {report_path}")
    
    return results


def evaluate_by_intent_type(intent_type: str, verbose: bool = True) -> Dict[str, Any]:
    """
    Evaluate queries of a specific intent type.
    
    Args:
        intent_type: One of 'schema', 'validation', 'sql', 'relationship'
        verbose: Whether to print progress
    
    Returns:
        Evaluation results for that intent type
    """
    test_queries = get_test_queries_by_type(intent_type)
    
    if verbose:
        print(f"\nEvaluating {len(test_queries)} {intent_type.upper()} queries...")
    
    return evaluate_system(test_queries=test_queries, verbose=verbose)


if __name__ == "__main__":
    # Run full evaluation
    results = run_full_evaluation(save_report=True)
    
    # Also evaluate by type
    print(f"\n{'='*80}")
    print(f"EVALUATION BY INTENT TYPE")
    print(f"{'='*80}\n")
    
    for intent_type in ['schema', 'validation', 'sql', 'relationship']:
        print(f"\n{intent_type.upper()}:")
        results = evaluate_by_intent_type(intent_type, verbose=False)
        if 'metrics' in results:
            for metric, score in results['metrics'].items():
                print(f"  {metric}: {score:.3f}")
