import pytest
from pathlib import Path
from ingestion.get_transcript import clean_filename
from ingestion.reader import parse_transcript_header, read_transcript_file


def test_clean_filename():
    unsafe_title = 'Capacity To Ship Packages: Within D Days? <LeetCode|875>'
    safe = clean_filename(unsafe_title)
    assert '<' not in safe
    assert '>' not in safe
    assert ':' not in safe
    assert '|' not in safe
    assert '?' not in safe
    assert safe == "Capacity To Ship Packages Within D Days LeetCode875"


def test_parse_transcript_header(tmp_path: Path):
    pattern_dir = tmp_path / "Binary Search"
    pattern_dir.mkdir(parents=True, exist_ok=True)
    sample_file = pattern_dir / "01_Test_Video.txt"

    content = (
        "VIDEO TITLE: Binary Search on Answer Space\n"
        "VIDEO ID: test_vid_123\n"
        "LANGUAGE: en\n"
        "URL: https://www.youtube.com/watch?v=test_vid_123\n\n"
        "================================================================================\n\n"
        "Hello everyone, welcome back.\n"
        "Today we check monotonic feasibility.\n"
    )
    sample_file.write_text(content, encoding="utf-8")

    source, text = parse_transcript_header(sample_file)
    assert source.video_id == "test_vid_123"
    assert source.video_title == "Binary Search on Answer Space"
    assert source.pattern == "Binary Search"
    assert "Today we check monotonic feasibility." in text

    payload = read_transcript_file(sample_file)
    assert payload["source"].video_id == "test_vid_123"
    assert "welcome back" in payload["transcript_text"]
