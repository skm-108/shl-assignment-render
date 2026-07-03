# Approach Document

## Summary

This project uses a deterministic Python controller around a hybrid retrieval stack. The conversation policy is state-machine driven, while the LLM only drafts user-facing language from retrieved catalog items.

## Why This Stack

- FastAPI gives the exact API surface the evaluator expects.
- BM25 and vector search together cover exact catalog names and semantic role descriptions.
- Metadata filtering prevents obviously invalid candidates from reaching the LLM.
- A cross-encoder reranker improves ordering among near-duplicate product families.
- A deterministic state machine makes clarification, refinement, comparison, and refusal predictable under replay.

## What Did Not Work In Early Analysis

- Treating the catalog as clean JSON is not safe; the source needs tolerant loading.
- Relying on the LLM to decide search behavior would be too unstable for the 8-turn evaluator.
- Treating report products as standalone assessments would blur the catalog relationships.

## How Improvement Will Be Measured

- Exact schema compliance on every response.
- Recall@10 on final committed recommendations.
- Trace replay success on the 10 public examples.
- Pass rate on hidden-style probes for refusal, refinement, comparison, and injection resistance.

## Implementation Notes

- All recommendations will come from validated catalog items only.
- Comparison answers will be grounded in catalog metadata, not generic model prior.
- The service will remain stateless across chat requests.
- Logging will capture state transitions, filters, retrieval results, and final shortlisted items.