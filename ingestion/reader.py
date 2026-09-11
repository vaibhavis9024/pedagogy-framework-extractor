from pathlib import Path
from typing import Tuple, Dict, Any

from extraction.schema import Source


def parse_transcript_header(file_path: Path) -> Tuple[Source, str]:
    """
    Parses a saved transcript file's header metadata and separates it from the text body.
    
    Returns:
        Tuple[Source, str]: (Source object containing video_id, video_title, pattern, and transcript_text)
    """
    path = Path(file_path)
    pattern_category = path.parent.name

    video_title = f"video_{path.stem}"
    video_id = path.stem
    lines = []

    with open(path, "r", encoding="utf-8") as f:
        content_lines = f.readlines()

    header_ended = False
    body_lines = []

    for line in content_lines:
        if not header_ended:
            if line.startswith("VIDEO TITLE:"):
                video_title = line.replace("VIDEO TITLE:", "").strip()
            elif line.startswith("VIDEO ID:"):
                video_id = line.replace("VIDEO ID:", "").strip()
            elif line.startswith("=" * 10):
                header_ended = True
            continue

        body_lines.append(line)

    transcript_text = "".join(body_lines).strip()

    source = Source(
        video_id=video_id,
        video_title=video_title,
        pattern=pattern_category,
    )

    return source, transcript_text


def read_transcript_file(file_path: Path) -> Dict[str, Any]:
    """
    Reads transcript file and returns a payload dictionary ready for Layer 2 extraction.
    """
    source, text = parse_transcript_header(file_path)
    return {
        "source": source,
        "transcript_text": text,
    }
