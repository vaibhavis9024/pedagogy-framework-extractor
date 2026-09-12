import pytest
from pydantic import ValidationError
from extraction.schema import (
    ExtractionResult,
    Evidence,
    PedagogicalPattern,
    Source,
    TopicFramework,
)


def test_source_creation():
    src = Source(
        video_id="abc123id",
        video_title="Binary Search Question Demonstration",
        pattern="Binary Search",
    )
    assert src.video_id == "abc123id"
    assert src.video_title == "Binary Search Question Demonstration"
    assert src.pattern == "Binary Search"


def test_source_missing_field():
    with pytest.raises(ValidationError) as exc_info:
        Source(video_id="abc123id", video_title="Title missing pattern")
    assert "pattern" in str(exc_info.value)


def test_evidence_creation():
    src = Source(
        video_id="vid1",
        video_title="Binary Search on Answer 1",
        pattern="Binary Search",
    )
    ev = Evidence(
        text="Let's assume this is our answer...",
        source=src,
    )
    assert ev.text == "Let's assume this is our answer..."
    assert ev.source.video_id == "vid1"


def test_evidence_missing_source():
    with pytest.raises(ValidationError) as exc_info:
        Evidence(text="Excerpt without source")
    assert "source" in str(exc_info.value)


def test_topic_framework_with_evidence():
    src1 = Source(video_id="vid1", video_title="Ship Packages", pattern="Binary Search")
    ev1 = Evidence(text="Check feasibility helper function", source=src1)
    
    tf = TopicFramework(
        name="Binary Search on Answer Space",
        trigger_condition="When finding minimum/maximum value satisfying monotonic condition",
        steps_checks=["Identify search space", "Check feasibility function"],
        example_problem="Capacity To Ship Packages Within D Days",
        evidence=[ev1],
    )
    assert tf.name == "Binary Search on Answer Space"
    assert len(tf.evidence) == 1
    assert tf.evidence[0].source.video_id == "vid1"


def test_topic_framework_multiple_sources():
    src1 = Source(video_id="vid1", video_title="Ship Packages", pattern="Binary Search")
    src2 = Source(video_id="vid2", video_title="Koko Eating Bananas", pattern="Binary Search")
    
    ev1 = Evidence(text="Check feasibility for shipping capacity...", source=src1)
    ev2 = Evidence(text="Check feasibility for eating speed...", source=src2)
    
    tf = TopicFramework(
        name="Binary Search on Answer Space",
        trigger_condition="Monotonic answer space search",
        steps_checks=["Define range [low, high]", "Binary search mid", "Check feasibility"],
        example_problem="Capacity To Ship Packages / Koko Eating Bananas",
        evidence=[ev1, ev2],
    )
    assert len(tf.evidence) == 2
    assert tf.evidence[0].source.video_id == "vid1"
    assert tf.evidence[1].source.video_id == "vid2"


def test_pedagogical_pattern_with_evidence():
    src = Source(video_id="vid1", video_title="Ship Packages", pattern="Binary Search")
    ev = Evidence(text="First let's dry run this test case on paper...", source=src)
    
    pp = PedagogicalPattern(
        pattern_name="Dry Run Before Coding",
        description="Teacher steps through example manually on array before writing code",
        when_used="Introduced before writing the final optimal code solution",
        evidence=[ev],
    )
    assert pp.pattern_name == "Dry Run Before Coding"
    assert len(pp.evidence) == 1
    assert pp.evidence[0].source.video_id == "vid1"


def test_extraction_result_multi_source():
    src1 = Source(video_id="vid1", video_title="Binary Search 1", pattern="Binary Search")
    src2 = Source(video_id="vid2", video_title="Binary Search 2", pattern="Binary Search")
    
    ev1 = Evidence(text="Excerpt from video 1...", source=src1)
    ev2 = Evidence(text="Excerpt from video 2...", source=src2)
    
    tf = TopicFramework(
        name="Binary Search on Answer Space",
        trigger_condition="Monotonic search space",
        steps_checks=["Steps..."],
        example_problem="Sample problem",
        evidence=[ev1, ev2],
    )
    pp = PedagogicalPattern(
        pattern_name="Guess and Refine",
        description="Propose naive approach then optimize",
        when_used="Start of problem discussion",
        evidence=[ev1],
    )
    
    res = ExtractionResult(
        topic_frameworks=[tf],
        pedagogical_patterns=[pp],
    )
    assert len(res.topic_frameworks) == 1
    assert len(res.topic_frameworks[0].evidence) == 2
    assert res.topic_frameworks[0].evidence[0].source.video_id == "vid1"
    assert res.topic_frameworks[0].evidence[1].source.video_id == "vid2"
