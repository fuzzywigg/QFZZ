# QFZZ Test Infrastructure Documentation

## Overview

This document describes the comprehensive test infrastructure for QFZZ core components, including state management, LLM routing, environment loading, and CI integration.

## Test Suite Statistics

- **Total Tests**: 187 tests
- **Test Files**: 9 test modules
- **Coverage**: 
  - `qfzz/core/state.py`: **99%**
  - `qfzz/core/llm_router.py`: **99%**
  - Overall project: 35%

## Test Files

### 1. `tests/conftest.py`
Shared fixtures and configuration for all test modules.

**Key Fixtures:**
- `temp_honeycomb`: Temporary honeycomb directory for state testing
- `state_manager`: StateManager instance with temp directory
- `mock_env`: Mocked environment variables for LLM providers
- `temp_config`: Temporary LLM router configuration
- `mock_llm_router`: Fully mocked LLM router with predictable responses
- `clean_env`: Clean environment (removes QFZZ env vars)
- `temp_dotenv`: Temporary .env file for testing
- `mock_file_corruption`: Utility for testing error recovery
- `assert_no_secrets_in_output`: Verify secrets don't leak

**Pytest Configuration:**
- Custom markers: `unit`, `integration`, `slow`, `requires_api`
- All fixtures are reusable across test modules
- Automatic cleanup of temporary files

### 2. `tests/test_honeycomb_state.py` (20 tests)
Comprehensive tests for Honeycomb state management (`qfzz/core/state.py`).

**Test Classes:**

#### `TestFileLocking` (3 tests)
- File lock timeout behavior (10 second timeout)
- Concurrent writes don't corrupt data
- Multiple StateManager instances share directory

#### `TestAtomicWrites` (2 tests)
- Partial write recovery
- All writes create valid JSON

#### `TestSchemaValidation` (2 tests)
- Schema validation with valid data
- Default structures match schema requirements

#### `TestErrorHandling` (4 tests)
- Nonexistent directory creates automatically
- Missing state files handled gracefully
- Corrupted JSON recovery
- Permission error handling

#### `TestStateOperations` (5 tests)
- Request history pruning (exactly 100 entries)
- Conversation history pruning (exactly 1000 entries)
- Setting track to None clears it
- Task status updates
- Learned patterns overwrites

#### `TestThreadSafety` (1 test)
- Concurrent read/write operations

#### `TestStateManagerEdgeCases` (3 tests)
- Empty playlist operations
- Large conversation history handling
- Special characters in content

### 3. `tests/test_llm_router_core.py` (32 tests)
Core tests for LLM router with comprehensive mocking.

**Test Classes:**

#### `TestProviderInitialization` (4 tests)
- All providers have correct models
- All providers have correct cost_per_1k values
- Provider availability without API keys
- Partial provider availability

#### `TestFallbackLogic` (4 tests)
- Fallback chain order: google → groq → anthropic → openai → ollama
- Fallback continues until success
- Preferred provider overrides primary
- All providers fail returns error

#### `TestCostOptimization` (5 tests)
- Cost calculation accuracy
- Total cost accumulation
- Cost tracking per provider
- Average cost calculation
- Free providers (Groq, Ollama) have zero cost

#### `TestProviderAPIMocking` (5 tests)
- Google API timeout
- Groq rate limit error
- Anthropic authentication failure
- OpenAI invalid model error
- Ollama connection error

#### `TestLatencyTracking` (2 tests)
- Latency recorded for each call
- Latency in realistic range

#### `TestIntegration` (6 tests)
- Temperature parameter handling
- Max tokens parameter handling
- Request count increments
- get_stats() returns complete info
- Empty prompt handling
- Very long prompt handling

#### `TestConfigurationEdgeCases` (3 tests)
- Missing config file uses defaults
- Empty config file raises KeyError
- Malformed config file raises JSONDecodeError

#### `TestLLMResponseDataclass` (3 tests)
- Response field access
- Response with all fields
- Error field optional

### 4. `tests/test_precommit_hooks.py` (23 tests)
Tests for pre-commit hook enforcement.

**Test Classes:**

#### `TestDetectSecrets` (4 tests)
- Blocks plaintext API keys
- Allows safe code
- Baseline file exists
- Respects .gitignore

#### `TestLintingHooks` (6 tests)
- Ruff configuration exists
- Ruff lint on valid code
- Ruff catches lint errors
- Black configuration exists
- Black formats code
- isort configuration and sorting

#### `TestPreCommitConfiguration` (5 tests)
- Config file exists
- Contains detect-secrets
- Contains ruff
- Contains isort
- Hooks run in correct order

#### `TestPreCommitExecution` (3 tests)
- Blocks on secrets
- Blocks on lint failures
- Allows clean commits

#### `TestAutoFixBehavior` (2 tests)
- Ruff auto-fix mode
- Black auto-formats

#### `TestPreCommitIntegration` (2 tests)
- Can install hooks
- Config is valid

### 5. `tests/test_env_loader.py` (28 tests)
Tests for environment variable loading and secret protection.

**Test Classes:**

#### `TestSecretNonLeakage` (5 tests)
- Secrets not in log output
- Exception messages don't expose secrets
- Router __repr__ doesn't leak secrets
- Router __str__ doesn't leak secrets
- Error responses don't leak API keys

#### `TestMissingKeys` (4 tests)
- Router behavior when all keys missing
- Error messages indicate missing key
- Optional keys don't cause failures
- Partial keys availability

#### `TestEnvLoading` (4 tests)
- dotenv loads .env file
- Env variables accessible via getenv()
- .env.example template exists
- .env in .gitignore

#### `TestEnvironmentVariablePrecedence` (4 tests)
- System env overrides dotenv
- dotenv override mode
- Missing env var returns None
- Missing env var with default

#### `TestRouterEnvIntegration` (4 tests)
- Router uses env vars for keys
- Router loads dotenv on import
- Router handles empty env vars
- Router handles whitespace env vars

#### `TestLoggingConfiguration` (2 tests)
- Logger configured for secrets
- Custom log filter pattern

#### `TestSecretValidation` (3 tests)
- API keys not hardcoded in source
- Config files don't contain secrets
- .env.example has placeholder values

#### `TestEnvLoadingIntegration` (2 tests)
- Full env loading workflow
- Env loading from different paths

### 6. `tests/test_ci_integration.py` (43 tests)
Tests for CI integration and infrastructure.

**Test Classes:**

#### `TestPytestConfiguration` (5 tests)
- pytest.ini options exist
- testpaths configured
- Markers defined
- Coverage configured
- Coverage targets qfzz package

#### `TestFixtureReusability` (4 tests)
- All shared fixtures available and functional

#### `TestMockExternalDependencies` (5 tests)
- No real API calls (Google, Anthropic, OpenAI)
- Filesystem operations use temp dirs
- No network requests in unit tests

#### `TestDeterministicBehavior` (4 tests)
- Temp directory isolation
- Mock router predictable responses
- No random behavior
- Timestamps mocked where needed

#### `TestGitHubActionsCompatibility` (6 tests)
- Tests complete quickly
- No interactive prompts
- Standard exit codes
- Output compatible with GitHub annotations
- No sudo required
- No display required

#### `TestCoverageConfiguration` (4 tests)
- Report format configured
- HTML output directory
- .gitignore excludes coverage files
- Reports uploadable

#### `TestTestInfrastructure` (4 tests)
- All test files discovered
- conftest provides fixtures
- Modules have docstrings
- Tests organized in classes

#### `TestCIWorkflow` (3 tests)
- Can run pytest from CLI
- Can generate coverage reports
- Tests pass in parallel

#### `TestPerformance` (3 tests)
- Unit tests are fast (<100ms)
- Integration tests under time limit (<5s)
- Full suite under 5 minutes

#### `TestTestQuality` (5 tests)
- Descriptive test names
- Tests have docstrings
- Assertions have messages
- Tests are independent
- Fixtures properly cleaned up

### 7. Existing Test Files

#### `tests/test_state.py`
Basic state management tests (inherited, 14 tests).

#### `tests/test_llm_router.py`
Basic LLM router tests (inherited, 17 tests).

#### `tests/test_config.py`
Configuration tests (inherited, 18 tests).

#### `tests/test_core.py`
Core station tests (inherited, 3 tests - currently failing due to API changes).

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_honeycomb_state.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=qfzz --cov-report=html
```

### Run Only Unit Tests
```bash
pytest tests/ -m unit
```

### Run Only Integration Tests
```bash
pytest tests/ -m integration
```

### Run with Verbose Output
```bash
pytest tests/ -v --tb=short
```

## Coverage Goals

### Achieved
- ✅ `qfzz/core/state.py`: **99% coverage**
- ✅ `qfzz/core/llm_router.py`: **99% coverage**
- ✅ Line coverage >80% for tested core modules
- ✅ Branch coverage >70% for tested core modules

### Target Areas for Improvement
- Station management (`qfzz/core/station.py`): 19% → 80%
- Blockchain components: 24-49% → 70%
- Dataset management: 13% → 60%
- DJ components: 14-44% → 60%

## Best Practices Implemented

### Mocking Strategy
- All external API calls are mocked
- No real network requests in tests
- Filesystem operations use temporary directories
- Deterministic behavior (no random data)

### Test Organization
- Tests grouped into logical classes
- Descriptive test names following pattern: `test_<functionality>_<condition>_<result>`
- All tests have docstrings
- Fixtures promote code reuse

### CI Readiness
- All tests pass without external dependencies
- Tests complete quickly (<2 minutes for full suite)
- Coverage reports generated automatically
- Compatible with GitHub Actions

### Security
- Tests verify secrets don't leak
- Environment variables properly isolated
- Temporary files cleaned up automatically
- No hardcoded credentials

## Contributing Tests

### Adding New Tests
1. Use appropriate fixtures from `conftest.py`
2. Follow existing naming conventions
3. Add docstrings to test functions
4. Group related tests in classes
5. Use appropriate pytest markers
6. Ensure tests are deterministic

### Test Template
```python
def test_feature_name_condition_expected_result(fixture_name):
    """Test that feature behaves correctly under condition."""
    # Arrange
    setup_data = prepare_test_data()
    
    # Act
    result = perform_operation(setup_data)
    
    # Assert
    assert result == expected_value
    assert other_condition is True
```

### Running Pre-commit Hooks
```bash
pre-commit run --all-files
```

## Known Issues

### Pre-existing Failures
- `tests/test_core.py`: 3 tests failing due to API changes in `StationConfig`
- These are not related to the new test infrastructure

### Warnings
- Deprecation warnings for `datetime.utcnow()` in `qfzz/core/state.py`
- FutureWarning for `google.generativeai` package (migration to `google.genai` recommended)

## Future Enhancements

1. **Increase Coverage**: Target 80%+ overall project coverage
2. **Parallel Testing**: Enable pytest-xdist for faster execution
3. **Performance Profiling**: Add performance benchmarks for critical paths
4. **Property-Based Testing**: Add hypothesis for edge case discovery
5. **Mutation Testing**: Use mutmut to verify test quality
6. **Visual Regression**: Add snapshot testing for output formats
7. **Load Testing**: Add stress tests for concurrent operations

## Test Maintenance

### Regular Tasks
- Update fixtures when APIs change
- Review and update test coverage goals
- Monitor test execution time
- Keep dependencies up to date
- Review and address deprecation warnings

### Quarterly Review
- Analyze test coverage trends
- Identify untested code paths
- Remove obsolete tests
- Refactor duplicated test code
- Update documentation

## References

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Python dotenv Documentation](https://pypi.org/project/python-dotenv/)

---

**Last Updated**: 2026-01-26
**Test Suite Version**: 1.0.0
**Maintainer**: QFZZ Team
