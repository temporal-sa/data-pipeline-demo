# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Install dependencies
uv sync                  # Base dependencies only
uv sync --extra dev      # Include development dependencies

# Environment configuration  
cp .env.example .env     # Copy example environment file
```

### Code Quality
```bash
# Using uv directly
uv run ruff check .      # Lint code
uv run ruff format .     # Format code  
uv run mypy .            # Type check

# Using just (recommended)
just check-all           # Run all quality checks (lint + format + typecheck)
just lint               # Lint only
just format             # Format only  
just typecheck          # Type check only
```

### Running the Application
```bash
# Start Temporal dev server
just temporal-start      # or: temporal server start-dev

# Run worker and UI (in separate terminals)
just worker             # or: uv run worker.py
just ui                 # or: uv run ui/app.py
```

### Workflow Operations
```bash
# Start workflow with scenario
just start-workflow <SCENARIO> <JOB_ID>

# Query workflow progress
just query-workflow <JOB_ID>

# Send signal to workflow
just signal-workflow <JOB_ID>

# Get workflow status
just workflow-status <JOB_ID>
```

## Architecture Overview

### Core Components

**Temporal Workflows:**
- `DataPipelineWorkflowHappyPath.py` - Standard workflow implementation
- `DataPipelineWorkflowScenarios.py` - **Dynamic workflow** that handles multiple scenarios via workflow type routing

**Activities:**
- `activities.py` - Extract, Transform, Load, and validation activities
- Activities use heartbeats and are designed for retryability

**Client & Worker:**
- `client.py` - Temporal client with optional TLS and payload encryption support
- `worker.py` - Dual-worker setup (distribution queue + unique task queues)

**UI:**
- `ui/app.py` - Flask web interface for triggering workflows
- `ui/templates/` - Web templates for job management

### Key Patterns

**Dynamic Workflows:**
The `DataPipelineWorkflowScenarios` class uses `@workflow.defn(dynamic=True)` to handle multiple scenario types in a single workflow definition. **Critical requirement:** Must import `Sequence` from `typing`, not `collections.abc`, for proper Temporal SDK compatibility.

**Worker Architecture:**
- Distribution worker handles workflow routing via `get_available_task_queue` activity
- Individual workers handle activities on unique task queues for load balancing
- Random task queue generation prevents worker collisions

**Scenario Routing:**
Scenarios are determined by workflow type and include:
- `DataPipelineAdvancedVisibility` - Custom search attributes
- `DataPipelineHumanInLoopSignal` - Manual intervention via signals
- `DataPipelineHumanInLoopUpdate` - Manual intervention via updates
- `DataPipelineIdempotency` - Duplicate activity execution testing
- `DataPipelineRecoverableFailure` - Exception handling and retry
- `DataPipelineNonRecoverableFailure` - Validation failure scenarios

**Data Flow:**
1. UI submits job → Distribution worker
2. Distribution worker assigns unique task queue
3. Workflow executes: Validate → Extract → Transform → Load → Poll
4. Activities use file-based data processing in `demodata/` directories

### Environment Configuration

**Local Development:** Uses `localhost:7233` by default

**Temporal Cloud:** Requires environment variables:
- `TEMPORAL_HOST_URL` - Cloud endpoint
- `TEMPORAL_NAMESPACE` - Namespace
- `TEMPORAL_MTLS_TLS_CERT` - Certificate path
- `TEMPORAL_MTLS_TLS_KEY` - Private key path
- `ENCRYPT_PAYLOADS=true` - Optional payload encryption

### File Structure

- `/demodata/` - Data processing directories (source, working, output)
- `dataobjects.py` - Data classes and exceptions
- `encryption_codec.py` - Optional payload encryption codec