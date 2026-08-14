---
description: RAG (retrieval-augmented generation) rules — only relevant if the project has a RAG pipeline
globs: ai/**, rag/**, retrieval/**, embeddings/**, vector/**, ingestion/**, knowledge/**
activation: glob
---

RAG architecture:
- Separate ingestion, parsing, chunking, embedding, indexing, retrieval,
  reranking, context assembly, and answer generation.
- Keep retrieval logic independent from answer generation logic.
- Preserve source metadata for traceability.

Rules:
- Never dump raw full documents into prompts when chunking is expected.
- Use deterministic chunking strategies unless explicitly experimenting.
- Maintain chunk metadata (source, page, section, title, tenant, timestamps).
- Prefer source attribution/citations in outputs when trust/traceability matters.
- Add configurable retrieval parameters: top_k, filters, score thresholds,
  reranking options.
- Ground answers in retrieved context. Handle no-context/low-confidence cases
  gracefully. Avoid hallucinating unavailable facts.

Do not:
- Mix ingestion code with runtime answer generation in the same module.
- Make retrieval behavior impossible to inspect or tune.
- Hide retrieval failures silently.
