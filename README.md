# SHL Conversational Assessment Recommender

Production-oriented FastAPI service for grounded SHL assessment recommendations.

## Scope

- Stateless `POST /chat` and `GET /health`
- Recommendations only from the SHL product catalog
- Clarification, refinement, comparison, and refusal behavior
- Strict response schema with no catalog hallucinations

## Documentation

- [Analysis](ANALYSIS.md)
- [Architecture](ARCHITECTURE.md)
- [Implementation Plan](IMPLEMENTATION_PLAN.md)
- [Prompting Strategy](PROMPTS.md)
- [Testing Strategy](TESTING.md)
- [Approach Document](APPROACH.md)

## Target Stack

- Python 3.12
- FastAPI
- Pydantic
- Sentence Transformers
- ChromaDB
- BM25
- Cross-encoder reranker
- Configurable LLM, with Gemini 2.5 Flash as the default target

## Initial Delivery Plan

1. Normalize and load the catalog with tolerant parsing.
2. Build deterministic conversation state and constraint extraction.
3. Add hybrid retrieval and reranking.
4. Expose the API and lock the response schema.
5. Build trace replay tests and adversarial probes.
