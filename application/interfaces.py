"""
Layer 3 — Application Interfaces & Data Contracts

Defines the architectural boundary between Layer 2 (Knowledge Base) and Layer 3 (Application).
Layer 3 receives new DSA questions (which do not originate from Pratyush's videos), retrieves relevant 
TopicFrameworks and PedagogicalPatterns from Layer 2, and generates step-by-step explanations in Pratyush's teaching style.

NOTE: This file defines abstract protocols and data models for Layer 3 integration.
Full LLM solver / retrieval execution belongs to future stages.
"""

from typing import List, Protocol
from pydantic import BaseModel, Field

from extraction.schema import PedagogicalPattern, TopicFramework


class NewQuestionInput(BaseModel):
    """
    Represents a new, novel DSA problem statement provided by a student.
    This question has no associated YouTube video source.
    """
    title: str = Field(description="Title or short description of the new DSA problem")
    problem_statement: str = Field(description="Full text of the problem statement")
    constraints: List[str] = Field(default_factory=list, description="Problem constraints (e.g. array length, value ranges)")


class ApplicationResult(BaseModel):
    """
    Represents the output of Layer 3: an explanation of the new problem constructed using retrieved 
    topic frameworks and pedagogical teaching patterns.
    """
    question: NewQuestionInput
    matched_frameworks: List[TopicFramework]
    matched_patterns: List[PedagogicalPattern]
    generated_explanation: str = Field(description="Step-by-step explanation generated in Pratyush's reasoning style")
    confidence_score: float = Field(description="Coverage / confidence score indicating framework match relevance")


class FrameworkRetriever(Protocol):
    """Abstract interface for retrieving matching TopicFrameworks for a new problem statement."""
    def retrieve_frameworks(self, question: NewQuestionInput, top_k: int = 3) -> List[TopicFramework]:
        ...


class PatternRetriever(Protocol):
    """Abstract interface for retrieving relevant PedagogicalPatterns for teaching a new problem."""
    def retrieve_patterns(self, question: NewQuestionInput, top_k: int = 3) -> List[PedagogicalPattern]:
        ...


class ExplanationGenerator(Protocol):
    """Abstract interface for generating an explanation in the source educator's teaching style."""
    def generate_explanation(
        self,
        question: NewQuestionInput,
        frameworks: List[TopicFramework],
        patterns: List[PedagogicalPattern],
    ) -> ApplicationResult:
        ...
