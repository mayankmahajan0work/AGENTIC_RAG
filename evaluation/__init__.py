"""
Evaluation module for RAG system quality assessment.

This module provides tools to evaluate the RAG system using RAGAS metrics:
- Context Precision: Relevance of retrieved documents
- Answer Relevancy: How well the answer addresses the question
- Faithfulness: Whether the answer is grounded in retrieved context
"""

from .test_queries import TEST_QUERIES, get_test_queries_by_type
from .ragas_eval import evaluate_system, run_full_evaluation
from .evaluation_report import generate_report, print_summary

__all__ = [
    'TEST_QUERIES',
    'get_test_queries_by_type',
    'evaluate_system',
    'run_full_evaluation',
    'generate_report',
    'print_summary'
]
