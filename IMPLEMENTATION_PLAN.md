# Implementation Plan

## Folder Structure

```text
app/
	api/
	agent/
	retrieval/
	catalog/
	models/
	services/
	utils/
tests/
docs/
data/
```

## Phase 1: Catalog Foundation

- Build a tolerant loader for the scraped catalog.
- Normalize names, durations, languages, job levels, and product classes.
- Derive aliases for family names and common abbreviations.
- Persist a clean internal catalog artifact for repeatable indexing.

## Phase 2: Retrieval Foundation

- Build embeddings for semantic search.
- Build BM25 over normalized text fields.
- Add metadata filtering for language, role level, and product class.
- Add cross-encoder reranking for final candidate ordering.

## Phase 3: Conversation Logic

- Implement the deterministic state machine.
- Implement intent and constraint extraction.
- Add clarification question selection rules.
- Add compare and refine paths that preserve prior shortlist intent.

## Phase 4: Response Generation

- Build prompt templates for clarify, recommend, compare, and refuse.
- Restrict the LLM to retrieved catalog items only.
- Validate every response against the required schema.

## Phase 5: API and Ops

- Implement `GET /health`.
- Implement `POST /chat` with the exact assignment response shape.
- Add structured logging and error handling.
- Add deployment configuration and startup checks.

## Phase 6: Verification

- Replay all 10 public traces as regression tests.
- Add hidden-style probes for prompt injection and off-topic requests.
- Validate recommendation count, schema compliance, and state transitions.
- Iterate on retrieval and ranking with measured trace outcomes.

## Delivery Order

1. Catalog loader and normalization.
2. Retrieval indexes.
3. State machine and constraint extraction.
4. Prompt builder and LLM wrapper.
5. API endpoints.
6. Tests and deployment docs.
