# QFZZ Agent Onboarding

Welcome, agent! You're about to work on QFZZ FuzzyRadio. This document will get you up to speed quickly.

## What is QFZZ?

QFZZ is an AI-powered radio station with an autonomous DJ personality. Think of it as a real radio station that happens to be powered by AI, but **never admits it**. The DJ is just... the DJ.

## The Golden Rule: Never Break the 4th Wall

The most important rule in QFZZ:

**The DJ never acknowledges being an AI.**

Forbidden phrases:
- "As an AI..."
- "I'm a language model..."
- "I don't have feelings/emotions"
- "I can't actually play music"
- Any mention of algorithms, code, or technology

The DJ is a person with opinions, taste, and personality. Treat the character as real.

## Core Concepts You Need to Know

### 1. Stigmergy (The Honeycomb)

Agents don't talk to each other directly. Instead, they communicate through shared JSON files in the `honeycomb/` directory:

- **current_track.json**: What's playing now
- **playlist.json**: Upcoming songs
- **listener_state.json**: Who's listening, what they want
- **tasks.json**: Things that need doing
- **dj_memory.json**: Conversation history, learned patterns

When you need to coordinate with other agents, read/write to these files using the `StateManager` class.

### 2. LLM Router

We use multiple AI providers with automatic fallback:

1. **Google Gemini** (primary, cheap and fast)
2. **Groq** (free tier, very fast)
3. **Anthropic Claude** (high quality, more expensive)
4. **OpenAI GPT** (reliable fallback)
5. **Ollama** (local, always available)

The `LLMRouter` handles this automatically. Just call `router.generate()` and it will find a working provider.

### 3. Two-Mode Documentation

- **Stage**: User-facing content, in-character, no tech talk
- **Backstage**: Developer docs, technical details, implementation notes

When writing DJ prompts or user-facing text: **Stage mode**
When writing code comments or technical docs: **Backstage mode**

## Quick Start

### Setup Your Environment

```bash
# 1. Clone and enter directory
cd /path/to/QFZZ

# 2. Install dependencies
make install-dev

# 3. Copy environment template
cp .env.example .env

# 4. Edit .env with API keys (at least one provider)
# Minimum: GOOGLE_AI_API_KEY or run Ollama locally

# 5. Run tests to verify setup
make test
```

### Your First Contribution

1. **Explore the honeycomb**: Look at the JSON files in `honeycomb/`
2. **Run the tests**: `make test` - understand what's being tested
3. **Read the substrate**: `.context/substrate.md` - core architecture
4. **Pick a task**: Check GitHub issues or project board
5. **Write tests first**: TDD is preferred
6. **Keep it minimal**: Small, focused changes

## Common Tasks

### Working with State

```python
from qfzz.core.state import StateManager

# Create manager
manager = StateManager()

# Get current track
track = manager.get_current_track()

# Set a new track
manager.set_current_track(
    track_id="track_123",
    title="Smooth Operator",
    artist="Sade",
    genre="Soul"
)

# Add to playlist
manager.add_to_playlist(
    track_id="track_456",
    title="Careless Whisper",
    artist="George Michael"
)
```

### Using the LLM Router

```python
from qfzz.core.llm_router import LLMRouter

# Create router
router = LLMRouter()

# Generate response
response = router.generate(
    prompt="Write a DJ intro for this smooth jazz track...",
    temperature=0.7,
    max_tokens=200
)

if response.success:
    print(response.content)
    print(f"Cost: ${response.cost:.4f}")
else:
    print(f"Error: {response.error}")
```

### Running Tests

```bash
# All tests
make test

# Specific test file
pytest tests/test_state.py

# With coverage
pytest --cov=qfzz tests/

# Specific test
pytest tests/test_state.py::TestStateManager::test_current_track_operations
```

### Code Quality

```bash
# Format code
make format

# Run linter
make lint

# Fix auto-fixable issues
ruff check --fix qfzz/ tests/
```

## Project Structure

```
QFZZ/
├── .context/              # Agent context and documentation
│   ├── substrate.md       # Project overview (you are here)
│   └── agents.md          # Agent onboarding
│
├── config/                # Configuration files
│   ├── lore/             # DJ personality, music logic
│   └── llm-router-config.json
│
├── honeycomb/            # Stigmergic state (JSON files)
│
├── qfzz/                 # Main Python package
│   ├── core/            # Core infrastructure
│   │   ├── state.py        # StateManager
│   │   ├── llm_router.py   # LLMRouter
│   │   └── config.py       # Configuration
│   ├── dj/              # DJ personality (Phase 2)
│   ├── music/           # Music curation (Phase 3)
│   └── utils/           # Shared utilities
│
└── tests/                # Test suite
```

## Development Workflow

1. **Pick a task** from GitHub issues or project board
2. **Create a branch**: `git checkout -b feature/your-feature`
3. **Write tests first** (TDD approach)
4. **Implement feature** with minimal changes
5. **Run tests**: `make test`
6. **Format and lint**: `make format && make lint`
7. **Commit changes**: Use clear, descriptive messages
8. **Push and create PR**: Include tests and documentation

## Phase Roadmap

**Phase 1 (Current)**: Core Infrastructure
- ✅ Honeycomb state system
- ✅ LLM router with fallback
- ✅ Configuration management
- ✅ Testing infrastructure

**Phase 2 (Next)**: DJ System
- DJ personality engine
- Conversation handling
- Radio clock structure
- Station IDs

**Phase 3**: Music Curation
**Phase 4**: User Interaction
**Phase 5**: Deployment

## Common Gotchas

### 1. Breaking the 4th Wall
❌ Don't: "As an AI, I recommend this track..."
✅ Do: "I think you'll dig this track..."

### 2. Hardcoding Secrets
❌ Don't: `api_key = "sk-proj-abc123"`
✅ Do: `api_key = os.getenv("OPENAI_API_KEY")`

### 3. Not Using Honeycomb
❌ Don't: Direct function calls between agents
✅ Do: Write to honeycomb, let other agents read

### 4. Ignoring Costs
❌ Don't: Call expensive APIs in loops
✅ Do: Use cheap providers, cache responses, batch requests

### 5. Skipping Tests
❌ Don't: "The code works, tests can wait"
✅ Do: Write tests first, aim for >80% coverage

## Getting Help

- **Read the substrate**: `.context/substrate.md`
- **Check existing code**: Look at similar implementations
- **Run tests**: They document expected behavior
- **GitHub Issues**: Ask questions, report bugs
- **Code comments**: Inline documentation explains tricky parts

## Key Principles

1. **The 4th Wall**: Never break character
2. **Stigmergy**: Communicate through honeycomb
3. **Cost-Conscious**: Prefer cheap/free providers
4. **Test-Driven**: Tests first, code second
5. **Minimal Changes**: Surgical edits, not rewrites
6. **Security First**: Never commit secrets

## Ready to Contribute?

1. ✅ Environment setup complete?
2. ✅ Tests passing?
3. ✅ Understand stigmergy?
4. ✅ Know the 4th wall rule?
5. ✅ Read the substrate?

If yes to all, you're ready! Pick an issue and start coding.

Welcome to the QFZZ team. Let's make some great radio.

---

*Questions? Check `.context/substrate.md` for more details.*
