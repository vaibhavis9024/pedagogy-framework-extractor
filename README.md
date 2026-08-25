# pedagogy-framework-extractor

A retrieval-augmented pipeline that extracts a teacher's *reasoning frameworks* from
video transcripts and applies them to new problems the source content never
covered — instead of retrieving and returning existing content.

## The problem

Most RAG systems answer questions the corpus already covers well: retrieve the
closest matching chunk, return it. That breaks down for a specific and common
learning scenario — you're studying from an educator whose teaching relies on
named heuristics and reasoning patterns (not just facts), and you hit a
question they never made a video on. Standard retrieval has nothing to return.

This project extracts the *underlying framework* — the trigger condition for
when a pattern applies, and the structure of how the teacher reasons through
it — rather than just chunks of transcript text, and applies that framework
to a novel problem in the same reasoning style.

## What makes this different from a standard RAG

- **Two-tier extraction, not flat chunking.** Frameworks are split into
  *topic-specific patterns* (e.g. a monotonicity check for binary search) and
  *cross-topic pedagogical style* (e.g. dry-running an example before coding,
  explaining via analogy, "guess → test → refine"). Naive chunking collapses
  both into unstructured text and loses the reusable structure.
- **Generalization over retrieval.** The hard case isn't "find the matching
  video" — it's producing a coherent explanation in the teacher's style for a
  problem with no direct match in the corpus.
- **Confidence-aware generation.** A coverage/confidence check flags when a
  new problem doesn't cleanly match any extracted framework, rather than
  silently generating a plausible-sounding but ungrounded explanation.
- **Validated against manual extraction.** Frameworks were first hand-extracted
  from transcripts to establish a ground-truth schema, then automated
  extraction was diffed against that baseline to measure real extraction
  quality — not just eyeballed for plausibility.

## Architecture (in progress)

1. **Transcript ingestion** — pulls public video transcripts as raw text.
2. **Manual baseline extraction** — human-authored ground truth for a subset
   of source material, used to validate automated extraction quality.
3. **Automated framework extraction** — LLM-based extraction into a structured
   schema (`topic_frameworks`, `pedagogical_patterns`), diffed against the
   manual baseline.
4. **Application / generation** — given a new, uncovered problem, retrieves
   the closest-matching framework(s) and generates an explanation in the
   source teacher's reasoning style.
5. **Confidence / coverage check** — flags low-confidence matches instead of
   forcing a style-transfer that isn't actually grounded in an extracted
   pattern.

## Scope and data note

The pipeline is teacher-agnostic by design — it takes any transcript corpus
and a target style as input. It was built and is demonstrated against one
educator's publicly available YouTube content, used for personal,
non-commercial study. **Scraped transcripts are not committed to this repo**;
only the pipeline code and a small illustrative/demo dataset are included.
This is a personal learning tool, not a hosted or multi-user product.

## Status

Early stage — starting with a single topic (Binary Search) to validate the
extraction → generation → confidence-check pipeline end to end before
expanding topic or source coverage.

## Stack

- Transcript retrieval: `youtube-transcript-api`
- Extraction / generation: LLM API (structured JSON output)
- Similarity / coverage check: sentence embeddings
