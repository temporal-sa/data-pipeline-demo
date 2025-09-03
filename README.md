# Temporal Data Pipeline Demo

_Leveraging the Temporal Python SDK_

This demo illustrates how to build a data pipeline with Temporal using the Python SDK. It features a web UI and CLI interface for executing ETL workflows with various scenario demonstrations including error handling, human-in-the-loop patterns, and advanced visibility features.

| Prerequisites      |    | Features       |    | Patterns            |    |
|:-------------------|----|----------------|----|---------------------|----|
| Network Connection | ✅ | Schedule       |    | Entity              |    |
| GitHub Actions     |    | Local Activity | ✅ | Long-Running        | ✅ |
| Python 3.12        | ✅ | Timer          |    | Fanout              |    |
| uv 0.4+            | ✅ | Signal         | ✅ | Continue As New     |    |
| | ✅ | Query          | ✅ | Manual Intervention | ✅ |
| |    | Heartbeat      | ✅ | Long-polling        |    |
|                    |    | Update         |    | Polyglot            |    |
|                    |    | Retry          | ✅ |                     |    |
|                    |    | Data Converter | |                     |    |
|                    |    | Codec Server   | |                     |    |
|                    |    | Custom Attrs   | ✅ |                     |    |
|                    |    | Worker Metrics |    |                     |    |
|                    |    | Side Effect    |    |                     |    |

## Quick Start Installation

### Prerequisites

* Python >= 3.10
* [uv package manager](https://docs.astral.sh/uv/)
* [Temporal CLI](https://docs.temporal.io/cli) for local development
* [Temporal Cloud account](https://cloud.temporal.io/) (optional, for production demos)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd temporal-data-pipeline-demo
   ```

2. **Install dependencies**
   ```bash
   # Install base dependencies
   uv sync
   
   # For development (includes linting/type checking tools)
   uv sync --extra dev
   ```

3. **Configure environment**
   ```bash
   # Copy example configuration
   cp .env.example .env
   
   # Edit .env with your settings (see Environment Configuration section)
   ```

4. **Start Temporal server**
   ```bash
   # For local development
   temporal server start-dev
   
   # Or using just
   just temporal-start
   ```

5. **Start the worker** (in a new terminal)
   ```bash
   uv run worker.py
   
   # Or using just
   just worker
   ```

6. **Start the UI** (in another terminal)
   ```bash
   uv run ui/app.py
   
   # Or using just
   just ui
   ```

7. **Access the demo**
   - Web UI: [http://localhost:5000](http://localhost:5000)
   - Temporal Web UI: [http://localhost:8233](http://localhost:8233)

## Demo Scenarios

### Web UI Demo Path

The web interface provides an intuitive way to demonstrate Temporal workflows to customers and attendees.

#### Basic Demo Flow

1. **Navigate to the Web UI** at [http://localhost:5000](http://localhost:5000)

2. **Submit a Job**
   - Select a scenario from the dropdown menu
   - Enter a unique Job ID (or use the generated one)
   - Click "Submit Job" to start the workflow

3. **Monitor Progress**
   - The job progress page shows real-time workflow execution
   - Progress bar updates as activities complete
   - View detailed logs and status information

4. **Explore Temporal Web UI**
   - Open [http://localhost:8233](http://localhost:8233)
   - Show workflow history, activity details, and timeline
   - Demonstrate workflow replay and debugging capabilities

#### Available Scenarios

**HappyPath** - Standard successful workflow execution
- Demonstrates basic ETL pipeline (Extract → Transform → Load)
- Shows activity heartbeats and progress tracking
- Good starting point for new audiences

**AdvancedVisibility** - Custom search attributes and workflow metadata
- Demonstrates search attribute updates during execution
- Shows how to make workflows discoverable and queryable
- Highlight business intelligence and monitoring capabilities

**HumanInLoopSignal** - Manual intervention using Signals
- Workflow pauses and waits for external signal
- Demonstrate sending signals via CLI or Web UI
- Shows how to handle external dependencies and approvals

**HumanInLoopUpdate** - Manual intervention using Updates
- Similar to Signal but with synchronous response
- Show the difference between Signals (fire-and-forget) and Updates (request-response)
- Demonstrate workflow interaction patterns

**Idempotency** - Duplicate activity execution
- Shows how Temporal handles duplicate activities automatically
- Demonstrate exactly-once execution guarantees
- Important for data consistency discussions

**RecoverableFailure** - Transient error handling
- Workflow encounters temporary failures and retries
- Demonstrate automatic retry policies and exponential backoff
- Show how workflows recover from infrastructure issues

**NonRecoverableFailure** - Permanent failure handling
- Workflow fails due to business logic validation
- Demonstrate how to handle permanent errors gracefully
- Show workflow failure states and error propagation

**APIFailure** - External service failure simulation
- Simulates external API unavailability
- Demonstrate long-running retry strategies
- Show how Temporal handles external service dependencies

### CLI Demo Path

For technical audiences or detailed demonstrations, use the CLI interface.

#### Basic CLI Operations

1. **Start a workflow**
   ```bash
   # Using just (recommended)
   just start-workflow HappyPath demo-001
   
   # Using Temporal CLI directly
   temporal workflow start \
     --workflow-id "job-demo-001" \
     --type "DataPipelineHappyPath" \
     --task-queue "worker_specific_task_queue-distribution-queue" \
     --input '{"input_filename": "info.json", "foldername": "./demodata", "poll_or_wait": "poll", "validation": "orange", "scenario": "HappyPath", "key": "demo-001"}'
   ```

2. **Query workflow progress**
   ```bash
   just query-workflow demo-001
   
   # Or directly
   temporal workflow query --workflow-id "job-demo-001" --type "progress"
   ```

3. **Check workflow status**
   ```bash
   just workflow-status demo-001
   
   # Or directly
   temporal workflow describe --workflow-id "job-demo-001"
   ```

4. **Send signals (for HumanInLoopSignal scenario)**
   ```bash
   just signal-workflow demo-001
   
   # Or directly
   temporal workflow signal \
     --workflow-id "job-demo-001" \
     --name "load_complete_signal" \
     --input '"completed"'
   ```

#### Advanced CLI Demonstrations

**List all workflows**
```bash
temporal workflow list
```

**Show workflow history**
```bash
temporal workflow show --workflow-id "job-demo-001"
```

**Search workflows by scenario**
```bash
temporal workflow list --query 'WorkflowType = "DataPipelineAdvancedVisibility"'
```

**Cancel a running workflow**
```bash
temporal workflow cancel --workflow-id "job-demo-001"
```

**Terminate a workflow**
```bash
temporal workflow terminate --workflow-id "job-demo-001" --reason "Demo complete"
```

## Environment Configuration

### Local Development (Default)

No configuration needed. The demo uses `localhost:7233` by default.

### Temporal Cloud Configuration

Edit `.env` with your Temporal Cloud credentials:

```bash
# Temporal Cloud connection
TEMPORAL_HOST_URL=your-namespace.tmprl.cloud:7233
TEMPORAL_NAMESPACE=your-namespace

# mTLS certificates (required for Temporal Cloud)
TEMPORAL_MTLS_TLS_CERT=/path/to/your/cert.pem
TEMPORAL_MTLS_TLS_KEY=/path/to/your/key.key

# Optional: Enable payload encryption
ENCRYPT_PAYLOADS=true

# Optional: Custom task queue name
TEMPORAL_TASK_QUEUE=data-pipeline
```

## Demo Tips for Trade Shows

### Preparation

1. **Pre-start services** before the demo to avoid wait times
2. **Clear previous demo data** using `just reset`
3. **Have both Web UI and Temporal Web UI** open in browser tabs
4. **Prepare specific job IDs** that relate to your audience (e.g., "customer-demo-2024")

### Recommended Demo Flow

1. **Start with HappyPath** to show basic workflow execution
2. **Show Temporal Web UI** to highlight observability features
3. **Demonstrate RecoverableFailure** to show reliability features
4. **Use HumanInLoopSignal** to show workflow interaction
5. **Finish with AdvancedVisibility** to show enterprise features

### Key Talking Points

- **Reliability**: Workflows survive process crashes and infrastructure failures
- **Observability**: Complete history and real-time monitoring
- **Scalability**: Distributed execution with automatic load balancing
- **Developer Experience**: Simple Python code with powerful platform features
- **Business Logic Focus**: Temporal handles infrastructure concerns

## Development

### Code Quality

```bash
# Run all quality checks
just check-all

# Individual commands
just lint        # Lint code with ruff
just format      # Format code with ruff  
just typecheck   # Type check with mypy
```

### Utility Commands

```bash
just clean       # Clean up temporary files
just reset       # Stop services and clean up
```

### Project Structure

```
temporal-data-pipeline-demo/
├── activities.py                    # ETL activities (extract, transform, load)
├── client.py                       # Temporal client configuration
├── worker.py                       # Temporal worker setup
├── DataPipelineWorkflowHappyPath.py # Standard workflow
├── DataPipelineWorkflowScenarios.py # Dynamic workflow for all scenarios
├── dataobjects.py                  # Data classes and exceptions
├── encryption_codec.py             # Optional payload encryption
├── ui/                            # Flask web interface
│   ├── app.py                     # Web application
│   └── templates/                 # HTML templates
├── demodata/                      # Sample data files
│   ├── source/                    # Input data
│   ├── working/                   # Processing directory
│   └── output/                    # Results
└── justfile                       # Development commands
```

## Troubleshooting

### Common Issues

**Port conflicts**: If port 7233 is in use, stop other Temporal servers with `just temporal-stop`

**Worker not starting**: Ensure Temporal server is running first

**Module import errors**: Run `uv sync` to install missing dependencies

**TLS certificate errors**: Verify certificate paths in `.env` are correct and files are readable

### Support

For issues specific to this demo, check the logs in your terminal windows. For Temporal platform questions, refer to the [Temporal documentation](https://docs.temporal.io/).