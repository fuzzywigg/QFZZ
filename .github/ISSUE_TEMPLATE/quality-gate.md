---
name: Quality Gate
about: Quality assurance checkpoint before phase completion
title: '[QG] '
labels: 'quality-gate'
assignees: ''
---

## Phase
<!-- Which phase is this quality gate for? -->

## Quality Checklist

### Security
- [ ] Dependency vulnerability scan completed
- [ ] CodeQL analysis passed
- [ ] No critical security issues
- [ ] Authentication/authorization verified

### Testing
- [ ] Unit test coverage >80%
- [ ] Integration tests passing
- [ ] E2E tests for critical paths
- [ ] Performance benchmarks met

### Documentation
- [ ] API documentation complete
- [ ] Architecture docs updated
- [ ] README reflects changes
- [ ] Deployment guide current

### Code Quality
- [ ] All PRs reviewed and merged
- [ ] No TODO comments in production code
- [ ] Linting rules satisfied
- [ ] No known bugs in scope

## Blockers
<!-- List any issues preventing quality gate from passing -->

## Sign-off
<!-- Phase can proceed when all checklist items complete -->
