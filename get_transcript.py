import os
import re
import time
from pathlib import Path

import requests
from youtube_transcript_api import YouTubeTranscriptApi

from extract_video_ids import extract_video_ids

# ==================================================
# CONFIG
# ==================================================

OUTPUT_DIR = Path("transcripts")


# ==================================================
# 1. Helper: get YouTube video title
# ==================================================

def get_video_title(video_id):

    url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        html = response.text

        match = re.search(
            r"<title>(.*?)</title>",
            html,
            re.IGNORECASE
        )

        if match:
            return match.group(1).replace(
                " - YouTube", ""
            ).strip()

    except Exception as e:
        print(f"⚠️ Could not get title for {video_id}: {e}")

    return f"video_{video_id}"


# ==================================================
# 2. Helper: clean filename
# ==================================================

def clean_filename(title):

    # Remove characters Windows does not allow
    safe_title = re.sub(
        r'[<>:"/\\|?*]',
        '',
        title
    )

    # Remove excessive whitespace
    safe_title = re.sub(
        r'\s+',
        ' ',
        safe_title
    ).strip()

    return safe_title


# ==================================================
# 3. Main process
# ==================================================

def main():
    print("Extracting video IDs from playlist...")
    playlists = extract_video_ids()

    print(f"Loaded {len(playlists)} pattern categories.")

    total_videos = sum(len(video_ids) for video_ids in playlists.values())
    print(f"Total videos: {total_videos}")

    api = YouTubeTranscriptApi()

    # Process every pattern category in order defined by extract_video_ids
    for pattern, video_ids in playlists.items():

        print("\n" + "=" * 80)
        print(f"PATTERN: {pattern}")
        print(f"VIDEOS: {len(video_ids)}")
        print("=" * 80)

        # Create folder for this pattern
        pattern_dir = OUTPUT_DIR / pattern
        pattern_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # Process videos inside this pattern in exact order
        for index, video_id in enumerate(video_ids, start=1):

            print(
                f"\n[{index}/{len(video_ids)}] "
                f"Processing: {video_id}"
            )

            # --------------------------------------------------
            # Get video title
            # --------------------------------------------------

            title = get_video_title(video_id)

            print(f"Title: {title}")

            # --------------------------------------------------
            # Get transcript
            # --------------------------------------------------

            transcript = None
            language = None

            try:

                transcript = api.fetch(
                    video_id,
                    languages=["en"]
                )

                language = "en"

            except Exception:

                print("English transcript not found. Trying Hindi...")

                try:

                    transcript = api.fetch(
                        video_id,
                        languages=["hi"]
                    )

                    language = "hi"

                except Exception as e:

                    print(
                        f"❌ Transcript unavailable: {video_id}"
                    )
                    print(f"   Reason: {e}")

                    continue

            # --------------------------------------------------
            # Clean title
            # --------------------------------------------------

            safe_title = clean_filename(title)

            filename = (
                f"{index:02d}_{safe_title}.txt"
            )

            filepath = pattern_dir / filename

            # --------------------------------------------------
            # Save transcript
            # --------------------------------------------------

            url = (
                f"https://www.youtube.com/watch?v={video_id}"
            )

            with open(
                filepath,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(f"VIDEO TITLE: {title}\n")
                f.write(f"VIDEO ID: {video_id}\n")
                f.write(f"LANGUAGE: {language}\n")
                f.write(f"URL: {url}\n")
                f.write("\n")

                f.write("=" * 80)
                f.write("\n\n")

                for snippet in transcript:

                    f.write(
                        snippet.text + "\n"
                    )

            print(f"✅ Saved: {filepath}")

            # Small delay to avoid hammering YouTube
            time.sleep(0.5)

    print("\n" + "=" * 80)
    print("🎉 ALL TRANSCRIPTS PROCESSED")
    print("=" * 80)


if __name__ == "__main__":
    main()
