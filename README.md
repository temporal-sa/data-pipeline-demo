# Temporal Data Pipeline

_Leveraging the Temporal Python SDK_

| Prerequisites      |    | Features       |    | Patterns            |    |
|:-------------------|----|----------------|----|---------------------|----|
| Network Connection | ✅ | Schedule       |    | Entity              |    |
| GitHub Actions     |    | Local Activity | ✅ | Long-Running        | ✅ |
| Python 3.12        | ✅ | Timer          |    | Fanout              |    |
| Poetry 1.8.3       | ✅ | Signal         | ✅ | Continue As New     |    |
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

* Python >= 3.8
* [Poetry](https://python-poetry.org)
* [Local Temporal server running](https://docs.temporal.io/cli/server#start-dev) or [Temporal Cloud](https://cloud.temporal.io/)
* Set Environment
```
TEMPORAL_HOST_URL=helloworld.sdvdw.tmprl.cloud:7233
TEMPORAL_MTLS_TLS_KEY=/Users/ktenzer/certs/ca.key
TEMPORAL_MTLS_TLS_CERT=/Users/ktenzer/certs/ca.pem
TEMPORAL_TASK_QUEUE=data-pipeline
TEMPORAL_NAMESPACE=helloworld.sdvdw
```

With this repository cloned, run the following at the root of the directory:

    $ poetry install
    $ poetry update
    $ cd ui; poetry update

That loads all required dependencies. Then to run a sample, usually you just run it in Python. For example:

sample:

    $ poetry run python worker.py
    $ cd ui; poetry run python app.py

UI should be available at [http://localhost:5000](http://localhost:5000)