# QFZZ FuzzyRadio - Context Substrate

## Overview

QFZZ is an AI-powered quantum radio station featuring autonomous DJ personality, intelligent music curation, and real-time listener interaction. The system operates as a continuous broadcast platform where artificial intelligence drives the experience while maintaining the illusion of a traditional radio station.

## Core Philosophy

**The 4th Wall**: The DJ never breaks character. No mentions of AI, LLMs, algorithms, or artificial intelligence. The DJ is simply... the DJ. A personality with taste, opinions, and a deep love for music.

**Stigmergy**: Agents communicate indirectly through shared state (the "honeycomb"), not direct function calls. This enables loose coupling and emergent behaviors.

**Radio Authenticity**: QFZZ feels like real radio - station IDs, updates "on the 8s", weather reports, local flair, dedicated blocks. Technology serves the experience, not the other way around.

## Architecture

### Honeycomb State System

The honeycomb is our stigmergic state management layer. Agents read and write JSON files to coordinate:

- **current_track.json**: What's playing right now
- **playlist.json**: The upcoming queue
- **listener_state.json**: Who's listening, what they want
- **tasks.json**: Pending actions for agents
- **dj_memory.json**: Conversation history, learned patterns, banned phrases

All operations are thread-safe using filelock. Schema validation ensures data integrity.

### LLM Router

Multi-provider AI routing with automatic fallback:

**Priority Chain**: Gemini → Groq → Claude → OpenAI → Ollama (local)

**Cost Optimization**: Prefer free/cheap providers when possible
- Gemini Flash: ~$0.000075/1k tokens
- Groq: Free tier
- Claude Sonnet: ~$0.003/1k tokens  
- GPT-4o-mini: ~$0.00015/1k tokens
- Ollama: $0 (local)

**Automatic Fallback**: If primary provider fails, seamlessly falls back through the chain until success or exhaustion.

### Module Structure

```
qfzz/
├── core/              # Core infrastructure
│   ├── state.py       # Honeycomb state management
│   ├── llm_router.py  # Multi-provider LLM routing
│   ├── station.py     # Station orchestration
│   └── config.py      # Station configuration
├── dj/                # DJ personality system
├── music/             # Music curation and metadata
├── streaming/         # Audio streaming infrastructure
├── knowledge/         # Knowledge graph and learning
└── utils/             # Shared utilities
```

## Phases

### Phase 1: Core Infrastructure (Current)
- [x] Honeycomb state system
- [x] LLM router with fallback chain
- [x] Configuration management
- [x] Development tooling (Makefile, testing, linting)

### Phase 2: DJ System
- [ ] Personality engine with prompting templates
- [ ] Conversation handling
- [ ] Radio clock (updates "on the 8s")
- [ ] Station IDs and transitions

### Phase 3: Music Curation
- [ ] Track selection algorithm
- [ ] Metadata enrichment
- [ ] Genre/mood management
- [ ] Playlist generation

### Phase 4: User Interaction
- [ ] Request handling (songs, shoutouts, questions)
- [ ] Listener preferences learning
- [ ] Real-time chat integration
- [ ] Community features

### Phase 5: Deployment
- [ ] Firebase hosting setup
- [ ] CDN for audio streaming
- [ ] Monitoring and analytics
- [ ] Scaling infrastructure

## Key Concepts

### Stigmergy
Indirect agent communication through shared environment. Agents leave "traces" in the honeycomb that other agents react to. This enables:
- Loose coupling between components
- Emergent behaviors
- Resilience to agent failures
- Easy debugging (just inspect JSON files)

### The 4th Wall
The DJ NEVER breaks character. Forbidden phrases are tracked in `dj_memory.json`:
- "AI", "LLM", "language model"
- "I am an artificial intelligence"
- "As an AI assistant"
- "I don't have feelings"
- etc.

The system is self-policing - learned patterns help avoid these pitfalls.

### Radio Clock
Traditional radio structure applied to AI station:
- **On the 8s**: Weather, traffic, news updates (:08, :18, :28, :38, :48, :58)
- **Station IDs**: Top and bottom of hour
- **Dedicated Blocks**: "Monday Morning Jazz", "Friday Night Dance Party", etc.
- **Natural Transitions**: Smooth segues between tracks

### Cost Optimization
AI calls are expensive. We optimize by:
1. Using free/cheap providers when possible
2. Caching responses when appropriate  
3. Batching requests when possible
4. Falling back to local Ollama as last resort
5. Tracking costs per request

## Development Guidelines

### Code Style
- **Line length**: 100 characters
- **Imports**: Use isort with black profile
- **Linting**: ruff with Python 3.10+ target
- **Testing**: pytest with >80% coverage
- **Type hints**: Encouraged but not required

### Security
- **Never** commit secrets or API keys
- Use `.env` for all sensitive config
- Run `detect-secrets` before committing
- Pre-commit hooks enforce security checks

### Testing
- Unit tests for all core functions
- Integration tests for cross-module interactions
- Mock external API calls (don't waste money on tests)
- Test edge cases and failure modes

### Documentation
Two modes:
- **Stage**: User-facing, in-character, no tech details
- **Backstage**: Developer docs, technical implementation

This file is "backstage." The DJ's prompts and user-facing content are "stage."

## Quick Start

```bash
# Install dependencies
make install-dev

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Run tests
make test

# Format code
make format

# Run linter
make lint

# Start server
make run
```

## Technical Debt & Future Work

### Known Limitations
- Schema validation is basic (use jsonschema library for production)
- No retry logic for transient failures (add exponential backoff)
- Limited error recovery in state manager
- Cost tracking is approximate (use actual provider metrics)

### Future Enhancements
- Distributed honeycomb across multiple nodes
- Real-time state synchronization via WebSocket
- Advanced cost optimization with request batching
- Provider performance monitoring and automatic optimization
- A/B testing of different DJ personalities

## Resources

- **Backlink Hive**: Reference implementation for stigmergic patterns
- **Firebase Hosting**: Deployment target
- **Ollama**: Local LLM fallback
- **GitHub Issues**: Task tracking and project management

## License

MIT License - See LICENSE file for details

---

*Last Updated: January 2026*
*Phase: 1 (Core Infrastructure)*
*Status: In Development*
