# Data Pipeline example


These samples show how one might create a data pipeline.

## Usage

Prerequisites:

* Python >= 3.8
* [Poetry](https://python-poetry.org)
* [Local Temporal server running](https://docs.temporal.io/cli/server#start-dev) or [Temporal Cloud](https://cloud.temporal.io/)

With this repository cloned, run the following at the root of the directory:

    poetry install

That loads all required dependencies. Then to run a sample, usually you just run it in Python. For example:

sample:

    $ poetry run python worker.py
    $ cd ui; poetry run python app.py