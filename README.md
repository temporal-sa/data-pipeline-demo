# Data Pipeline example


These samples show how one might create a data pipeline.

## Usage

Prerequisites:

* Python >= 3.8
* [Poetry](https://python-poetry.org)
* [Temporal CLI installed](https://docs.temporal.io/cli#install)
* [Local Temporal server running](https://docs.temporal.io/cli/server#start-dev)

With this repository cloned, run the following at the root of the directory:

    poetry install

That loads all required dependencies. Then to run a sample, usually you just run it in Python. For example:

sample:

    poetry run python run_worker.py
    poetry run python start_data_pipeline.py

In separate terminals

You can also demonstrate it waiting for a signal with:

    poetry run python run_worker.py
    poetry run python start_data_pipeline_wait_signal.py
    poetry run python signal_load_complete.py

All in separate terminals.