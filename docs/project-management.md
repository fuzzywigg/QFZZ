# QFZZ Project Management

## Overview

QFZZ uses a phase-based development approach organized through a GitHub Project Board. This document describes the workflow, conventions, and best practices for managing work.

## Development Phases

### Phase 1: Core Infrastructure
**Focus**: Foundation components - QFZZStation, DatasetManager, BlockchainTrustNetwork, EdgeOptimizer

**Key Deliverables**:
- Station orchestrator with lifecycle management
- Dataset management with quality scoring
- Blockchain trust network
- Edge optimization infrastructure

### Phase 2: DJ System
**Focus**: PersonalizedDJ, conversational AI, trust building

**Key Deliverables**:
- DJ personality system
- User profile management
- LLM integration
- Recommendation engine foundation

### Phase 3: Music Curation
**Focus**: Content library, playlist generation, music player

**Key Deliverables**:
- Audio streaming implementation
- Playlist algorithms
- Content management
- Music player interface

### Phase 4: User Interaction
**Focus**: Frontend application, API layer, real-time features

**Key Deliverables**:
- Next.js application
- Authentication system
- API endpoints
- WebSocket integration

### Phase 5: Deployment
**Focus**: Production deployment, monitoring, edge distribution

**Key Deliverables**:
- Containerization
- CI/CD pipeline
- Monitoring infrastructure
- Edge deployment packages

## Project Board Structure

### 🔮 Latent Space (Discovery)
**Purpose**: Research, architectural exploration, technology evaluation

**When to use**:
- Investigating new technologies
- Architectural decision documentation
- Feasibility studies
- Open-ended exploration

**Criteria to move out**:
- Clear decision made
- Documentation created
- Actionable tasks identified

### 📥 Backlog (Ready)
**Purpose**: Well-defined tasks ready to be prioritized

**Entry criteria**:
- Clear description and acceptance criteria
- Dependencies identified
- Appropriate labels assigned
- Estimated effort (if available)

**Exit criteria**:
- Prioritized for upcoming sprint
- Assigned to phase milestone

### ✅ To Do (Next Sprint)
**Purpose**: Prioritized work for current/next sprint

**Entry criteria**:
- Sprint prioritization complete
- All blockers resolved
- Phase milestone assigned

**Exit criteria**:
- Developer assigned
- Work started

### 🚧 In Progress (Active Work)
**Purpose**: Currently being developed

**Entry criteria**:
- Developer assigned
- Branch created (if applicable)

**Exit criteria**:
- PR opened for review
- Implementation complete

### 👀 Review (Awaiting Feedback)
**Purpose**: Code review, testing, feedback collection

**Entry criteria**:
- PR created and linked
- Tests passing
- Ready for review

**Exit criteria**:
- PR approved and merged
- Issue resolved

### ✨ Done (Completed)
**Purpose**: Completed work (last 30 days visible)

**Entry criteria**:
- PR merged or issue closed
- Acceptance criteria met
- Documentation updated

## Label System

### Phase Labels (Mutually Exclusive)
- `phase-1: core` - Core Infrastructure
- `phase-2: dj` - DJ System
- `phase-3: music` - Music Curation
- `phase-4: user-interaction` - User Interaction
- `phase-5: deployment` - Deployment

### Type Labels (Can Combine)
- `latent-discovery` - Research and exploration
- `quality-gate` - Quality assurance checkpoint
- `documentation` - Documentation work
- `security` - Security-related
- `testing` - Testing and QA
- `blocked` - Blocked by dependency

### Priority (Optional)
Use GitHub issue priorities or custom labels:
- `priority: critical` - Must do now
- `priority: high` - Important
- `priority: medium` - Normal priority
- `priority: low` - Nice to have

## Milestone Usage

### Phase Milestones
Each phase has a milestone with:
- Target completion date
- Phase description
- Key deliverables

Assign issues to phase milestones to track progress.

### Special Milestones
- **Latent Space Review** - Research completion checkpoints
- **Quality Gate Checkpoint** - Recurring quality verification

## Workflow

### Starting New Work

1. **Discovery Phase**
   ```
   Create issue with latent-discovery label
   → Add to "🔮 Latent Space"
   → Research and document
   → Create actionable tasks when complete
   ```

2. **Implementation Phase**
   ```
   Create issue with phase label
   → Add to "📥 Backlog"
   → Prioritize in planning
   → Move to "✅ To Do"
   → Assign to developer
   → Auto-moves to "🚧 In Progress"
   ```

3. **Review Phase**
   ```
   Create PR linking issue
   → Auto-moves to "👀 Review"
   → Code review
   → Merge PR
   → Auto-moves to "✨ Done"
   ```

### Issue Templates

Use appropriate issue template:
- **Phase 1-5 Tasks** - Development work for specific phase
- **Latent Discovery** - Research and exploration
- **Quality Gate** - Quality assurance checkpoint

### Pull Request Conventions

**Title format**: `[Phase] Brief description`
- `[P1] Implement QFZZStation initialization`
- `[P2] Add PersonalizedDJ trust scoring`
- `[Discovery] Research LLM integration options`

**Description should include**:
- Problem being solved
- Approach taken
- Key changes
- Testing performed
- Related issues (auto-linked)

### Quality Gates

Before completing each phase:
1. Create quality gate issue
2. Run all quality checks
3. Document findings
4. Block phase milestone until passing
5. Sign-off and close

**Quality gate checklist**:
- Security scan (CodeQL, dependencies)
- Test coverage >80%
- Documentation complete
- No critical bugs
- Performance benchmarks met

## Best Practices

### Issue Creation
- Use descriptive titles
- Include clear acceptance criteria
- Add relevant labels and milestone
- Link related issues
- Estimate effort if possible

### Issue Management
- Keep issues small and focused
- One issue per feature/bug
- Update status regularly
- Close completed issues promptly
- Document decisions in comments

### Sprint Planning
- Review "📥 Backlog" regularly
- Prioritize based on phase roadmap
- Move high-priority items to "✅ To Do"
- Balance work across phases
- Consider dependencies

### Documentation
- Update docs with code changes
- Keep architecture docs current
- Document decisions in ADRs
- Link issues to relevant docs
- Include examples

## Communication

### Issue Discussions
- Use issue comments for technical discussion
- Tag relevant people with @mentions
- Keep conversations focused
- Document decisions in issue description

### Pull Request Reviews
- Review within 24-48 hours
- Provide constructive feedback
- Approve when ready
- Request changes when needed
- Thank reviewers

### Status Updates
- Update issue status regularly
- Comment on blockers immediately
- Share progress in sprint reviews
- Celebrate completions

## Metrics

Track these metrics for project health:
- **Velocity** - Issues completed per sprint
- **Cycle time** - Time from "To Do" to "Done"
- **WIP limit** - Max items "In Progress" (recommend 3-5)
- **Quality** - Issues reopened or bugs found
- **Coverage** - Test coverage percentage

## Phase Completion Criteria

Each phase is complete when:
- All milestone issues closed
- Quality gate passed
- Documentation updated
- Demo/showcase completed
- Team retrospective held
- Next phase planned

## References

- [Project Board Setup Guide](../.github/PROJECT_BOARD_SETUP.md)
- [Architecture Documentation](../ARCHITECTURE.md)
- [Feature Roadmap](../FEATURE_ROADMAP.md)
- [Contributing Guide](../CONTRIBUTING.md) (if exists)

---

**Document Status**: v1.0  
**Last Updated**: January 2026  
**Owner**: @fuzzywigg
