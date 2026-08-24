"""
Evaluation Framework for SIH PS 26117 Industrial Document & RAG Intelligence.
Provides standardized evaluation datasets, metrics, and automated runners.
"""

from evaluation.engine.evaluator import RAGEvaluator
from evaluation.engine.metrics import EvaluationMetrics

__all__ = ["RAGEvaluator", "EvaluationMetrics"]
