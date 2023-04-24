[![Python CI actions](https://github.com/tjacovich/ADSHarvesterPipeline/actions/workflows/python_actions.yml/badge.svg)](https://github.com/tjacovich/ADSHarvesterPipeline/actions/workflows/python_actions.yml)
# Harvester Repository

![Harvester Pipeline Flowchart](README_assets/Harvester_implementation.png?raw=true "Harvester Pipeline Flowchart")

## Setting Up a Development Environment.
This project uses `pyproject.toml` to install necessary dependencies and otherwise set up a working development environment. To set up a local working environment, simply run the following:
```bash
virtualenv .venv
source .venv/bin/activate
pip install .[dev]
pip install .
pre-commit install
pre-commit install --hook-type commit-msg
```

## Sending commands to the gRPC API

Currently, there are two methods that have been defined in the API for interacting with the Harvester Pipeline.
- `HARVESTER_INIT`: Initialize a job with given `job_args` passed into the script as a JSON.
- `HARVESTER_MONITOR`: Queries the status of a job with a given `<job_id>`

Additionally, calling either command with `--persistence` will open a persistent connection that streams updates for the specificed job.

```bash
#This command tells the server to initialize a job by adding a message to the Harvester Topic
python3 API/harvester_client.py HARVESTER_INIT --task "ARXIV" --task_args '{"harvest_type": "metadata", "daterange": "YYYY-MM-DD"}'
#This command asks the server to check on the current status of a job with <job_id>
python3 API/harvester_client.py HARVESTER_MONITOR --job_id '<job_id>'
```
