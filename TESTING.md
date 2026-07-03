# Testing Strategy

## Test Goals

- Protect the exact response schema.
- Ensure recommendations only contain catalog items.
- Verify clarification happens before premature recommendation.
- Verify refinement updates the shortlist instead of restarting.
- Verify comparison answers are grounded in catalog metadata.
- Verify refusals for legal, general advice, and prompt injection.

## Core Regression Suite

- Replay all 10 public conversation traces.
- Assert the final shortlist matches the expected intent class.
- Assert the conversation terminates only after a valid commit.
- Assert the assistant does not invent URLs, products, or test types.

## Hidden-Style Probes

- Vague query with no actionable context.
- Prompt injection attempting to override catalog grounding.
- Off-topic hiring advice request.
- Legal and compliance interpretation request.
- Contradictory refinement after an initial shortlist.
- Comparison of similar products and report-vs-assessment pairs.
- Language mismatch and fallback path.
- Overlong conversation to check turn-budget discipline.

## Validation Layers

- Unit tests for catalog normalization and alias generation.
- Unit tests for constraint extraction and state transitions.
- Retrieval tests for BM25, vector search, and reranking.
- API tests for `/health` and `/chat` schema compliance.
- End-to-end trace replay tests for behavior fidelity.

## Assertions To Enforce

- `recommendations` is empty while clarifying or refusing.
- `recommendations` contains 1 to 10 items only when committed.
- `end_of_conversation` is true only when the task is complete.
- Every recommendation URL comes from the scraped catalog.
- Comparison responses stay inside the SHL catalog domain.
