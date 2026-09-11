import json
import re

from yt_dlp import YoutubeDL

PLAYLIST_URL = (
    "https://www.youtube.com/playlist?list=PLbJhGqY-mq47k_WLUtzVjmarUm1EuXPj2"
)

# Defined pattern categories in Pratyush's DSA Sheet / Roadmap
PATTERNS = [
    "Two Pointers",
    "Sliding Window",
    "Binary Search",
    "Kadane",
    "Prefix Sum",
    "Merge Intervals",
    "Stack",
    "Monotonic Stack",
    "Queue",
    "Linked List",
    "Tree",
    "Binary Tree",
    "BST",
    "Graph",
    "Dynamic Programming",
    "Backtracking",
    "Heap",
    "Trie",
]


def extract_video_ids(playlist_url=PLAYLIST_URL):
    """
    Extracts flat video IDs from the YouTube playlist and categorizes them by DSA pattern.
    Returns a dictionary mapping pattern category names to lists of video IDs in order.
    """
    ydl_opts = {
        "extract_flat": True,
        "skip_download": True,
    }

    playlists = {pattern: [] for pattern in PATTERNS}
    playlists["Miscellaneous / Intro"] = []

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

        for entry in info.get("entries", []):

            if not entry:
                continue

            title = entry.get("title") or ""
            video_id = entry.get("id")

            if not title:
                print(
                    f"⚠️ Skipping video with missing title: {video_id}"
                )
                continue

            if not video_id:
                print(
                    f"⚠️ Skipping video with missing ID: {title}"
                )
                continue

            matched = False

            for pattern in PATTERNS:
                if re.search(
                    rf"\b{re.escape(pattern)}\b",
                    title,
                    re.IGNORECASE
                ):
                    playlists[pattern].append(video_id)
                    matched = True
                    break

            if not matched:
                playlists["Miscellaneous / Intro"].append(video_id)

    # Remove empty categories while preserving category order
    playlists = {
        k: v
        for k, v in playlists.items()
        if v
    }

    return playlists


if __name__ == "__main__":
    extracted_playlists = extract_video_ids()
    print(json.dumps(extracted_playlists, indent=4))
