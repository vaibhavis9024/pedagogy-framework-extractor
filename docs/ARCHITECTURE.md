# Pedagogy Framework Extractor — Architecture Specification

## 1. Project Purpose

The **Pedagogy Framework Extractor** is an intelligent teaching-knowledge extraction and generalization system. Standard Retrieval-Augmented Generation (RAG) systems retrieve existing text chunks to answer questions already present in a corpus. That approach fails when a student encounters a novel problem never covered in the source videos.

This project extracts an educator's underlying **problem-solving frameworks** and **pedagogical reasoning patterns** from video transcripts. Once extracted into a structured knowledge base, these patterns can be retrieved and applied to solve and explain **new, uncovered DSA problems** in the instructor's signature reasoning style.

---

## 2. Overall Architecture

The system is organized into a clean three-layer pipeline:

```text
Pratyush Videos
      │
      ▼
Raw Transcripts (Layer 1)
      │
      ▼
Extraction (Layer 2)
      │
      ▼
Structured Teaching Knowledge
      │
      ├────────────────────┐
      │                    │
      ▼                    ▼
Topic Frameworks     Pedagogical Patterns
      │                    │
      └──────────┬─────────┘
                 │
                 ▼
          Future Knowledge Base
                 │
                 ▼
          New DSA Question (Layer 3)
                 │
                 ▼
        Relevant Frameworks
                 │
                 ▼
       Relevant Teaching Patterns
                 │
                 ▼
             Application
                 │
                 ▼
             Explanation
```

---

## 3. Layer 1 — Raw Source Material

### Purpose
Layer 1 handles the collection, organization, and immutable storage of raw source material from YouTube videos.

### Contents & Metadata
Each raw source item contains:
- `video_id`: YouTube video ID string (e.g., `abc123id`)
- `video_title`: Title of the source video (scraped from YouTube)
- `pattern`: Playlist / category name (e.g., `Binary Search`, `Sliding Window`, `Two Pointers`)
- `transcript`: Verbatim transcript text (retrieved via `youtube-transcript-api`)

### Storage Structure
Raw transcripts are saved in `transcripts/{pattern}/{index}_{clean_title}.txt`. Each file contains header metadata lines followed by the transcript text:

```text
VIDEO TITLE: Capacity To Ship Packages Within D Days
VIDEO ID: abc123id
LANGUAGE: en
URL: https://www.youtube.com/watch?v=abc123id

================================================================================

[Transcript text lines follow...]
```

### Why Transcripts Are Kept Separate
Raw transcripts remain immutable reference material. Mixing extracted frameworks into transcript text files would corrupt the raw source data, prevent re-extraction with updated schemas or LLM models, and break provenance tracking.

---

## 4. Layer 2 — Extracted Teaching Knowledge

### Purpose
Layer 2 processes raw transcript text from Layer 1 and extracts structured, machine-readable teaching knowledge into two distinct categories:

1. **Topic Frameworks (`topic_frameworks`)**: Problem-solving knowledge, trigger conditions, steps/checks, and concrete example problems.
2. **Pedagogical Patterns (`pedagogical_patterns`)**: Educator teaching techniques, real-life analogies, guess-and-refine heuristics, and manual dry-run behaviors.

### Per-Video Extraction Prompt (`extraction/prompt.py`)
Layer 2 relies on a dedicated, maintainable prompt (`extraction/prompt.py`) designed to process **one transcript at a time**:
- **Per-Video Scope**: Extractions analyze a single transcript in isolation without assuming cross-video context. Cross-video deduplication and canonicalization take place in later pipeline stages.
- **Anti-Summarization Rules**: The prompt explicitly forbids video summarization, listing raw code snippets, or extracting generic textbook DSA knowledge unless demonstrated in the transcript.
- **Evidence Grounding**: Every extracted topic framework and pedagogical pattern must be supported by verbatim transcript excerpts (`evidence`) linked to the video's `Source` metadata. Unsupported claims are omitted rather than inferred.

### Pydantic Data Models (`extraction/schema.py`)

```python
class Source(BaseModel):
    video_id: str
    video_title: str
    pattern: str

class Evidence(BaseModel):
    text: str
    source: Source

class TopicFramework(BaseModel):
    name: str
    trigger_condition: str
    steps_checks: List[str]
    example_problem: str
    evidence: List[Evidence]

class PedagogicalPattern(BaseModel):
    pattern_name: str
    description: str
    when_used: str
    evidence: List[Evidence]

class ExtractionResult(BaseModel):
    topic_frameworks: List[TopicFramework]
    pedagogical_patterns: List[PedagogicalPattern]
```

### Provenance & Multi-Source Evidence
Frameworks and pedagogical patterns are recurring across multiple videos. Provenance is attached directly to each item in `evidence: List[Evidence]`. This design enables a single canonical framework to store supporting quotes from multiple videos without duplicating the framework itself or tying the entire extraction to a single source video.

---

## 5. Layer 3 — Application (Future Component)

### Purpose
Layer 3 receives a novel DSA problem statement submitted by a student (for which Pratyush has never made a video), retrieves matching frameworks and pedagogical patterns from Layer 2, and generates a step-by-step solution in Pratyush's teaching style.

### Why New Questions Do Not Have Source Videos
Layer 1 and Layer 2 learn *how Pratyush teaches* from his existing videos. A new question represents an unseen problem. It has no associated YouTube video source because the knowledge base is being applied to generalize onto novel inputs.

### Architectural Boundary (`application/interfaces.py`)
Layer 3 defines clean abstract protocols (`FrameworkRetriever`, `PatternRetriever`, `ExplanationGenerator`) and data models (`NewQuestionInput`, `ApplicationResult`) allowing future retrieval and generation engines to plug in cleanly without modifying Layer 1 or Layer 2.

---

## 6. Data Flow

```text
[YouTube Playlist]
       │
       ▼ (ingestion/extract_video_ids.py)
[Categorized Video IDs by Pattern]
       │
       ▼ (ingestion/get_transcript.py)
[Raw Transcript Files + Headers in transcripts/{pattern}/]
       │
       ▼ (ingestion/reader.py)
[Source Metadata + Transcript Payload]
       │
       ▼ (extraction/prompt.py + LLM call)
[ExtractionResult JSON (TopicFrameworks + PedagogicalPatterns + Evidence)]
       │
       ▼
[Structured Knowledge Base]
       │
       ▼ (application/interfaces.py)
[Layer 3 Retrieval & Explanation Engine] (Planned)
```

---

## 7. Separation of Responsibilities

- `ingestion/`: Layer 1 playlist video ID extraction, transcript retrieval, header parsing, file storage.
- `extraction/`: Layer 2 Pydantic schema validation (`schema.py`), system/user prompts (`prompt.py`).
- `application/`: Layer 3 data models (`NewQuestionInput`, `ApplicationResult`) and abstract protocol contracts (`interfaces.py`).
- `tests/`: Automated unit test suite verifying schema constraints, evidence provenance, and transcript parsing.
- `docs/`: Comprehensive architecture specifications and technical decision records.

---

## 8. Current Implementation Status

| Component | Status | Details |
| :--- | :--- | :--- |
| **Layer 1: Video ID Extraction** | **IMPLEMENTED NOW** | `ingestion/extract_video_ids.py` using `yt_dlp` |
| **Layer 1: Transcript Ingestion** | **IMPLEMENTED NOW** | `ingestion/get_transcript.py` using `youtube-transcript-api` |
| **Layer 1: Header & Source Parsing** | **IMPLEMENTED NOW** | `ingestion/reader.py` parsing headers into `Source` objects |
| **Layer 2: Pydantic Schema** | **IMPLEMENTED NOW** | `extraction/schema.py` with multi-source `Evidence` & `Source` |
| **Layer 2: Extraction Prompts** | **IMPLEMENTED NOW** | `extraction/prompt.py` enforcing strict transcript grounding |
| **Layer 3: Abstract Interfaces** | **IMPLEMENTED NOW** | `application/interfaces.py` defining protocol boundaries |
| **Layer 3: Vector RAG & LLM Solver** | **PLANNED / FUTURE** | Postponed until extraction quality baseline is established |
| **Framework Canonicalization** | **PLANNED / FUTURE** | Postponed until multi-video extractions are collected |

---

## 9. Future Planned Components

1. **Manual Baseline Diff Tool**: Automated comparison tool diffing LLM extraction results against human-authored ground truth extractions.
2. **Semantic Clustering & Canonicalization**: Aggregation pipeline merging similar frameworks across videos (e.g. "Binary Search on Answer Space").
3. **Vector Knowledge Base**: Embeddings index over `topic_frameworks` and `pedagogical_patterns` for similarity retrieval.
4. **Layer 3 Solver Engine**: LLM pipeline implementing `ExplanationGenerator` to solve novel DSA problems.

---

## 10. Explicitly What Is NOT Implemented Yet

- No vector database (Chroma, FAISS, Pinecone) has been added.
- No embedding model generation has been executed.
- No automated framework merging or clustering algorithms are active.
- No automated new-question solver LLM agent is executing in Layer 3.

---

## 11. Architectural Decisions

### Decision 1: Separation of Raw Transcripts from Extracted Knowledge
- **Reasoning**: Raw transcripts are immutable source artifacts. Keeping them separate ensures idempotency—extractions can be re-run, diffed against manual baselines, or processed with newer LLM schemas without altering raw data.

### Decision 2: Separation of Topic Frameworks and Pedagogical Patterns
- **Reasoning**: Problem-solving logic (e.g. binary search feasibility) is domain-specific knowledge, whereas teaching style (e.g. dry-running an array, guess-and-refine) is cross-domain pedagogical behavior. Separating them allows Layer 3 to combine a technical framework with any teaching pattern dynamically.

### Decision 3: Attaching Evidence to Extracted Knowledge
- **Reasoning**: LLM extractions can hallucinate generic textbook definitions. Requiring verbatim transcript excerpts (`evidence`) ensures every extracted framework is grounded in what the teacher actually said.

### Decision 4: Source Metadata inside Evidence
- **Reasoning**: Storing `source` (`video_id`, `video_title`, `pattern`) inside `Evidence` ensures complete traceability. A human evaluator can immediately verify an excerpt against the original YouTube video.

### Decision 5: Multi-Source Evidence Support (`List[Evidence]`)
- **Reasoning**: Educator Pratyush demonstrates key frameworks (like "Binary Search on Answer Space") across multiple distinct videos. Placing `Source` inside `Evidence` allows a single canonical framework to gather evidence from multiple videos without duplicating the framework model.

### Decision 6: New-Question Application Layer Requires No Source Video
- **Reasoning**: Layer 1/2 learn from Pratyush's videos. Layer 3 applies that learned knowledge to novel student questions that have no source video.

### Decision 7: Postponing Canonicalization & Merging
- **Reasoning**: Deduplicating frameworks prematurely before inspecting raw LLM extractions leads to loss of nuanced teaching patterns. Canonicalization will be designed after analyzing extraction outputs from multiple video batches.

### Decision 8: Postponing Vector RAG & Solver Engine
- **Reasoning**: Building a RAG engine on unvalidated extractions yields poor results. Establishing schema rigor, transcript ingestion stability, and extraction evaluation baseline first ensures the downstream RAG system operates on high-quality knowledge.
