"""
Layer 3 — Application to New Questions
Defines abstract interfaces and data contracts for retrieving learned teaching frameworks and applying them to new questions.
"""

from .interfaces import (
    NewQuestionInput,
    ApplicationResult,
    FrameworkRetriever,
    PatternRetriever,
    ExplanationGenerator,
)

__all__ = [
    "NewQuestionInput",
    "ApplicationResult",
    "FrameworkRetriever",
    "PatternRetriever",
    "ExplanationGenerator",
]
