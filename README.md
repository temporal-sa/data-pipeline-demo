# Temporal Data Pipeline

_Leveraging the Temporal Python SDK_

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


This demo illustrates how to build a simple data pipeline with Temporal using the Python SDK. It provides a simple UI which executes a pipeline as-a-workflow containing validation, extract, transform and load activities. 

## Usage

Prerequisites:

* Python >= 3.10
* [uv](https://docs.astral.sh/uv/)
* [Local Temporal server running](https://docs.temporal.io/cli/server#start-dev) or [Temporal Cloud](https://cloud.temporal.io/)

### Environment Setup

Copy the example environment file and configure your settings:

    $ cp .env.example .env

Then edit `.env` with your specific configuration. For Temporal Cloud, you'll need to set:
- `TEMPORAL_HOST_URL` - Your Temporal Cloud endpoint  
- `TEMPORAL_NAMESPACE` - Your namespace
- `TEMPORAL_MTLS_TLS_CERT` - Path to your certificate file
- `TEMPORAL_MTLS_TLS_KEY` - Path to your private key file
- `TEMPORAL_TASK_QUEUE` - Task queue name (defaults to "data-pipeline")
- `ENCRYPT_PAYLOADS` - Set to "true" to enable payload encryption (optional)

With this repository cloned, run the following at the root of the directory:

    $ uv sync

That installs all required dependencies. For development, install the dev dependencies:

    $ uv sync --extra dev

Then to run the sample:

    $ uv run worker.py
    $ uv run ui/app.py

UI should be available at [http://localhost:5000](http://localhost:5000)

## Development

### Code Quality

This project uses ruff for formatting and linting, and mypy for type checking:

    # Format code
    $ uv run ruff format .

    # Lint code
    $ uv run ruff check .

    # Type check
    $ uv run mypy .