# Architecture

## Design Principles

- Keep workflow deterministic in Python; let the LLM narrate, not decide.
- Treat catalog grounding as a hard constraint, not a prompt instruction.
- Prefer staged narrowing over one-shot recommendation.
- Separate base assessments from reports and solution bundles.

## System Flow

```text
Client
  |
FastAPI
  |
Conversation Controller
  |
State Machine
  |
Constraint Extraction
  |
Metadata Filter
  |
Hybrid Retrieval
  |-- BM25
  |-- Vector Search
  |
Cross-Encoder Reranker
  |
Prompt Builder
  |
LLM
  |
JSON Schema Validation
  |
Response
```

## Why Each Component Exists

- FastAPI: exposes the exact assignment endpoints with low overhead.
- Conversation controller: orchestrates one stateless turn from history alone.
- State machine: makes clarification, recommendation, refinement, comparison, and refusal deterministic.
- Constraint extraction: turns user language into structured filters and intent signals.
- Metadata filter: removes impossible candidates before expensive retrieval.
- BM25: captures exact catalog wording, abbreviations, and family names.
- Vector search: captures semantic role descriptions and paraphrases.
- Cross-encoder reranker: resolves ambiguity between close catalog neighbors.
- Prompt builder: constrains the LLM to retrieved items and the current state.
- LLM: writes the reply text and comparison explanation, but not the shortlist source.
- JSON validation: protects the evaluator contract.

## Domain Objects

- CatalogItem: normalized representation of one scraped product.
- ProductClass: assessment, report, solution bundle, or guide.
- ConversationState: UNKNOWN, CLARIFICATION, RECOMMEND, REFINE, COMPARE, REFUSE, COMPLETE.
- ConstraintSet: role, seniority, language, use case, stage, skills, duration, and exclusions.
- Recommendation: name, url, test_type only.

## Package Boundaries

- app/api: request and response schemas, route handlers.
- app/agent: state machine, intent classification, prompt orchestration.
- app/catalog: tolerant loading, normalization, aliasing, derived attributes.
- app/retrieval: filtering, BM25, embeddings, Chroma, reranking.
- app/services: LLM, embedding, and storage abstractions.
- app/models: Pydantic models and domain types.
- app/tests: trace replays and behavior probes.

## Key Design Trade-offs

- Determinism over cleverness: the system should be explainable under 8-turn replay.
- Hybrid retrieval over LLM search: catalog size and exact-match requirements justify it.
- Narrow shortlist over broad recall: final ranking can return up to 10, but the agent should not over-explain irrelevant items.
- Catalog-derived comparisons over generic comparisons: product families matter more than general assessment theory.
