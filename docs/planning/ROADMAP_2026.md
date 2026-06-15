# QFZZ Sovereign Radio: Strategic Roadmap 2026

**Mission**: To establish a fully sovereign, AI-driven broadcast ecosystem that operates without reliance on centralized gatekeepers, ensuring verified content ownership and immutable audit trails.

## Phase 1: Sovereign Foundation (Current - Q1 2026)

*Standardizing the infrastructure for 24/7 reliability.*

### Sprint 1.1: Ingestion Hardening (Completed)

- [x] **Strict Whitelist Implementation**: Enforced verified domains (`archive.org`, `freemusicarchive.org`) to mitigate copyright liability.
- [x] **Smart Metadata Parsing**: Heuristics for direct MP3 downloads to eliminate "Unknown Artist" artifacts.
- [x] **Agentic Terminal UI**: Deployed `HiveTerminal` for interactive user feedback.
- [x] **Security Baseline Set**: Dependabot vulnerability alerts and automated security fixes confirmed enabled, with security modernization labels applied.

### Sprint 1.2: Broadcast Stability (Next Priority)

- [ ] **Icecast Migration**: Transition from Python `http.server` to **Icecast 2** for production-grade streaming, buffering, and concurrent listener support.
  - *Why*: The current Python server cannot scale. Icecast is the industry standard for open radio.
- [ ] **Dockerization**: Containerize the `Source Client` (the logic generating the stream) and the `Icecast Server` for one-click deployment.
- [ ] **Ledger Verification Tool**: Create a utility to validate the SHA-256 hash chain of `qfzz_ledger.json` to prove no tampering has occurred.

## Phase 2: Agentic Evolution (Q2 2026)

*Transforming from a "Jukebox" to a "Sentient Station".*

### Sprint 2.1: The "Deep" DJ

- [ ] **LLM Integration**: Replace the mock terminal responses with a local LLM (e.g., Llama 3 running on `ollama`) that reads `qfzz_knowledge_graph.json` to generate context-aware commentary.
- [ ] **Semantic Segues**: The DJ should explicitly reference the *relationship* between tracks (e.g., "That was Kai Engel, leading us into another track in the Key of C#...").

### Sprint 2.2: Hive Logic

- [ ] **Request Arbitration**: Users can request songs, but the AI "Queen" decides based on the current "Vibe" (stored in `ledger` state).
- [ ] **Knowledge Graph Expansion**: Automatically fetch artist bios from Wikipedia (using the whitelist) to populate the graph nodes.

## Phase 3: Commercialization & Portfolio (Q3 2026)

*Packaging the technology for value and demonstration.*

### Sprint 3.1: "Project as Product" (Resume Artifacts)

- [ ] **Architecture Diagram**: Visual map of the "Sovereign Stack" (Local LLM + Ledger + Icecast + React Frontend).
- [ ] **Demo Reel**: A polished 2-minute video demonstrating the "Agentic Workflow" (Requesting a song -> AI negotiating -> Playback).
- [ ] **Case Study**: "Building a Copyright-Compliant AI Radio on the Edge."

### Sprint 3.2: Business Viability

- [ ] **White-Label Licensing**: Packaging the QFZZ stack for other niche communities who want their own "Sovereign Radio".
- [ ] **Sovereign Ad Injection**: A protocol for inserting "Sovereign Ads" (promotions for local/community goods) that are cryptographically verified in the ledger.

## Living Document Status

*Last Updated: Jan 25, 2026*
*Status: Active Planning*
