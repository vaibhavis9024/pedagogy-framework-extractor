from pydantic import BaseModel, Field
from typing import List


class Source(BaseModel):
    video_id: str = Field(
        description="The YouTube video ID associated with the transcript"
    )

    video_title: str = Field(
        description="The title of the source video"
    )

    pattern: str = Field(
        description=(
            "The playlist or pattern category from which the video came "
            "(e.g., 'Binary Search')"
        )
    )


class Evidence(BaseModel):
    text: str = Field(
        description="Short excerpt from the source transcript directly supporting the extraction"
    )

    source: Source = Field(
        description="The source video metadata from which this evidence excerpt came"
    )


class TopicFramework(BaseModel):
    name: str = Field(
        description="Name of the problem-solving framework"
    )

    trigger_condition: str = Field(
        description=(
            "Description of the type of problem or "
            "condition that triggers use of this framework"
        )
    )

    steps_checks: List[str] = Field(
        description=(
            "Ordered steps, checks, or reasoning process "
            "used when applying the framework"
        )
    )

    example_problem: str = Field(
        description=(
            "A concrete problem from the transcript "
            "where this framework is demonstrated"
        )
    )

    evidence: List[Evidence] = Field(
        description=(
            "List of supporting evidence excerpts with their source video metadata."
        )
    )


class PedagogicalPattern(BaseModel):
    pattern_name: str = Field(
        description="Name of the teaching pattern"
    )

    description: str = Field(
        description="Description of how the teaching pattern is used"
    )

    when_used: str = Field(
        description="When or under what circumstances the teaching pattern is used"
    )

    evidence: List[Evidence] = Field(
        description=(
            "List of supporting evidence excerpts with their source video metadata."
        )
    )


class ExtractionResult(BaseModel):
    topic_frameworks: List[TopicFramework]

    pedagogical_patterns: List[PedagogicalPattern]