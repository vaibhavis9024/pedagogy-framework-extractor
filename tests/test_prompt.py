import pytest
from extraction.prompt import (
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    build_extraction_prompt,
    format_user_prompt,
)
from extraction.schema import Source


def test_format_user_prompt_with_source_model():
    source = Source(
        video_id="test_vid_123",
        video_title="Capacity To Ship Packages Within D Days",
        pattern="Binary Search",
    )
    transcript_text = "Today we discuss binary search on answer space..."

    user_prompt = format_user_prompt(source, transcript_text)
    assert "Video ID: test_vid_123" in user_prompt
    assert "Video Title: Capacity To Ship Packages Within D Days" in user_prompt
    assert "Pattern Category: Binary Search" in user_prompt
    assert transcript_text in user_prompt


def test_format_user_prompt_with_dict():
    source_dict = {
        "video_id": "dict_vid_456",
        "video_title": "Sliding Window Maximum",
        "pattern": "Sliding Window",
    }
    transcript_text = "We use a monotonic deque to track max..."

    user_prompt = format_user_prompt(source_dict, transcript_text)
    assert "Video ID: dict_vid_456" in user_prompt
    assert "Video Title: Sliding Window Maximum" in user_prompt
    assert "Pattern Category: Sliding Window" in user_prompt
    assert transcript_text in user_prompt


def test_format_user_prompt_invalid_type():
    with pytest.raises(ValueError) as exc_info:
        format_user_prompt("invalid_string_type", "sample text")
    assert "source must be a Source model or a dictionary" in str(exc_info.value)


def test_build_extraction_prompt_structure():
    source = Source(
        video_id="abc123id",
        video_title="Koko Eating Bananas",
        pattern="Binary Search",
    )
    transcript_text = "Let's test eating speeds from 1 to max..."

    prompt_bundle = build_extraction_prompt(source, transcript_text)

    assert "system_prompt" in prompt_bundle
    assert "user_prompt" in prompt_bundle

    sys_prompt = prompt_bundle["system_prompt"]
    usr_prompt = prompt_bundle["user_prompt"]

    # Verify anti-summarization instructions
    assert "DO NOT PRODUCE A VIDEO SUMMARY OR PROBLEM STATEMENT DIGEST" in sys_prompt

    # Verify category instructions
    assert "TOPIC FRAMEWORKS" in sys_prompt
    assert "PEDAGOGICAL PATTERNS" in sys_prompt

    # Verify grounding instructions
    assert "EVIDENCE GROUNDING & PROVENANCE" in sys_prompt

    # Verify per-video scope
    assert "PER-VIDEO EXTRACTION ONLY" in sys_prompt

    # Verify schema keys in instructions match ExtractionResult
    assert '"topic_frameworks"' in sys_prompt
    assert '"pedagogical_patterns"' in sys_prompt
    assert '"trigger_condition"' in sys_prompt
    assert '"steps_checks"' in sys_prompt
    assert '"example_problem"' in sys_prompt
    assert '"evidence"' in sys_prompt
    assert '"pattern_name"' in sys_prompt
    assert '"when_used"' in sys_prompt

    # Verify user prompt contains dynamic metadata
    assert "Video ID: abc123id" in usr_prompt
    assert "Video Title: Koko Eating Bananas" in usr_prompt


def test_system_prompt_has_no_hardcoded_video_metadata():
    # Ensure system prompt does not hardcode dynamic video metadata
    assert "abc123id" not in SYSTEM_PROMPT
    assert "Koko Eating Bananas" not in SYSTEM_PROMPT
