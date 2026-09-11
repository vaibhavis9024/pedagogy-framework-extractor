"""
Layer 1 — Raw Source Material Ingestion
Provides YouTube playlist video extraction, transcript downloading, and header/metadata reading.
"""

from .extract_video_ids import extract_video_ids
from .get_transcript import main as download_transcripts
from .reader import read_transcript_file, parse_transcript_header

__all__ = [
    "extract_video_ids",
    "download_transcripts",
    "read_transcript_file",
    "parse_transcript_header",
]
