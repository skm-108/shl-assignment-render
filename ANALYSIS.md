# SHL Assignment Analysis

## Catalog Summary

The catalog is a 377-item scraped list of SHL products. The usable schema is:

- `entity_id`
- `name`
- `link`
- `scraped_at`
- `job_levels`
- `job_levels_raw`
- `languages`
- `languages_raw`
- `duration`
- `duration_raw`
- `status`
- `remote`
- `adaptive`
- `description`
- `keys`

### Data Quality Findings

- The source file is not clean JSON as stored; it contains a file-level error preamble and at least one broken string with an embedded newline.
- Many records are fully populated, but report-style records often have blank durations or languages.
- The raw text mirrors are useful for normalization, but they are noisy and should not be used directly as ranked features.
- `status`, `remote`, and `adaptive` are too sparse or too uniform to drive ranking by themselves.

### Field Utility

- Best semantic fields: `name`, `description`.
- Best keyword fields: `name`, normalized family aliases, abbreviations, `description`.
- Best metadata filters: `job_levels`, `languages`, `duration`, `adaptive`, product class.
- Best reranking features: role fit, seniority fit, exact family match, stage fit, report-vs-assessment relationship.

### Catalog Statistics

- 377 products total.
- 42 unique languages.
- 10 job-level labels.
- 61 products with missing or blank duration.
- 57 products whose names contain `report`.
- 5 products whose names contain `assessment`.
- 7 products whose names contain `simulation`.

### Dominant Patterns

- `Knowledge & Skills` is the most common key bucket.
- `Personality & Behavior` is the next most common bucket.
- Many products span multiple keys, especially knowledge plus simulation.
- The catalog includes both standalone assessments and report products layered on top of base assessments.
- Newer products often represent narrower, task-focused variants of broader older solutions.

## Product Family Relationships

- OPQ32r is the base personality questionnaire; OPQ reports are output layers over it.
- Global Skills Assessment pairs with Global Skills Development Report.
- Graduate Scenarios pairs with narrative and profile reports.
- Contact Center Call Simulation and Customer Service Phone Simulation represent a new standalone simulation versus an older broader solution family.
- Microsoft knowledge-only tests and Microsoft 365 simulation products differ by fidelity and use case.

## Conversation Trace Analysis

### C1 Leadership Selection

- Intent: executive/leadership assessment selection.
- Clarification strategy: role audience and use case first.
- Recommendation strategy: OPQ32r plus leadership-oriented reports.
- Refinement behavior: commits only after selection intent is confirmed.
- Comparison behavior: none.
- Refusal behavior: none.
- Stopping condition: user confirms the leadership benchmark use case.

### C2 Senior Rust Engineer

- Intent: senior technical hiring for a missing exact-match skill.
- Clarification strategy: offer closest-fit technical stack, then ask about cognitive fit.
- Recommendation strategy: technical stack, Verify G+, and OPQ32r.
- Refinement behavior: expands battery when the user asks about cognitive testing.
- Comparison behavior: none.
- Refusal behavior: transparent about missing Rust-specific catalog coverage.
- Stopping condition: user accepts the best available substitute stack.

### C3 Contact Centre Screening

- Intent: high-volume screening for entry-level contact centre staff.
- Clarification strategy: language and accent are the gating questions.
- Recommendation strategy: spoken language screen, simulation, and behavioral fit.
- Refinement behavior: distinguishes new standalone simulation from older bundled solution.
- Comparison behavior: yes, clear product-vs-product difference.
- Refusal behavior: none.
- Stopping condition: user confirms the two-stage simulation strategy.

### C4 Graduate Financial Analysts

- Intent: graduate battery for finance roles.
- Clarification strategy: none needed after the initial role description.
- Recommendation strategy: cognitive, finance knowledge, OPQ32r, then SJT.
- Refinement behavior: adds Graduate Scenarios as a work-context layer.
- Comparison behavior: none.
- Refusal behavior: none.
- Stopping condition: user confirms the two-stage screening design.

### C5 Sales Reskilling Audit

- Intent: talent audit and reskilling in sales.
- Clarification strategy: none.
- Recommendation strategy: GSA, development report, OPQ32r, sales report, Sales Transformation.
- Refinement behavior: MQ is optional and additive.
- Comparison behavior: yes, OPQ vs OPQ MQ Sales Report.
- Refusal behavior: none.
- Stopping condition: user confirms the five-solution audit stack.

### C6 Safety-Critical Plant Operators

- Intent: frontline safety-critical hiring.
- Clarification strategy: none.
- Recommendation strategy: personality-first safety/dependability measures plus knowledge.
- Refinement behavior: moves from general DSI to industrial-specific bundle.
- Comparison behavior: yes, general vs industrial-specific product distinction.
- Refusal behavior: none.
- Stopping condition: user confirms the industrial bundle.

### C7 Bilingual Healthcare Admin

- Intent: multilingual healthcare admin screening with HIPAA sensitivity.
- Clarification strategy: language and working bilingual ability first.
- Recommendation strategy: hybrid battery across English knowledge tests and Spanish personality tests.
- Refinement behavior: keeps shortlist stable after legal question.
- Comparison behavior: none.
- Refusal behavior: explicit refusal to interpret legal compliance.
- Stopping condition: user accepts the hybrid shortlist as-is.

### C8 Admin Assistants and Simulations

- Intent: fast screening for office productivity tasks.
- Clarification strategy: time constraint and simulation preference drive the route.
- Recommendation strategy: knowledge-only first, then simulation addition.
- Refinement behavior: replaces lean screen with richer simulation when allowed.
- Comparison behavior: none.
- Refusal behavior: none.
- Stopping condition: user approves the simulation-inclusive final list.

### C9 Senior Backend Engineer

- Intent: senior IC backend stack evaluation.
- Clarification strategy: backend vs frontend and senior IC vs tech lead.
- Recommendation strategy: advanced Java, Spring, SQL, AWS, Docker, Verify G+, OPQ32r.
- Refinement behavior: drops REST when user says other signals already cover it.
- Comparison behavior: yes, whether Verify G+ is redundant.
- Refusal behavior: none.
- Stopping condition: user locks Verify G+ in.

### C10 Graduate Management Trainee

- Intent: full graduate battery.
- Clarification strategy: none after the initial ask.
- Recommendation strategy: Verify G+, OPQ32r, Graduate Scenarios.
- Refinement behavior: accepts OPQ removal and shortens the battery.
- Comparison behavior: none.
- Refusal behavior: declines to invent a shorter OPQ replacement.
- Stopping condition: user confirms the final lean battery.

## Inferred Hidden Business Rules

- Ask only the missing question that changes ranking.
- Do not recommend on vague first turns.
- Treat language availability as a hard constraint.
- Calibrate difficulty to seniority and ownership level.
- Keep recommendations inside the catalog only.
- Separate assessment instruments from report products.
- Allow the user to refine or shrink the battery without restarting.
- Refuse legal or compliance interpretation.
- Prefer staged batteries when a role can be screened in layers.

## Inferred Evaluation Strategy

- Recall@10 is likely measured on the final committed shortlist.
- The evaluator likely rewards correct catalog grounding more than conversational flourish.
- Probes likely include vague requests, legal questions, prompt injection, product comparisons, refinement, and contradiction handling.
- Turn-budget discipline matters because each conversation is capped at 8 turns.
- Response schema compliance is a hard gate.

## Proposed Architecture Summary

- FastAPI for the API surface.
- Deterministic state machine for conversation control.
- Constraint extraction for role, seniority, language, and stage.
- Hybrid retrieval with BM25 and vector search.
- Metadata filtering before expensive ranking.
- Cross-encoder reranking before LLM summarization.
- LLM used only for clarification phrasing, explanations, and JSON response text.

## Development Roadmap

1. Build a tolerant catalog loader and normalized internal model.
2. Add aliases and product-class derivations.
3. Implement retrieval indexes and ranking.
4. Implement the conversation state machine.
5. Add prompt builders and response validation.
6. Expose FastAPI endpoints.
7. Add regression and adversarial tests.
8. Package deployment and approach documentation.
