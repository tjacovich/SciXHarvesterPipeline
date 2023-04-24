[![Python CI actions](https://github.com/tjacovich/ADSHarvesterPipeline/actions/workflows/python_actions.yml/badge.svg)](https://github.com/tjacovich/ADSHarvesterPipeline/actions/workflows/python_actions.yml)
# Harvester Repository

![Harvester Pipeline Flowchart](README_assets/Harvester_implementation.png?raw=true "Harvester Pipeline Flowchart")

## Setting Up a Development Environment.
Running `docker-compose up --build -d --force-recreate` will stand up a docker container with supervised instances of the harvester mock pipeline and the gRPC server. For full functionality, a postgres database needs to be setup and provisioned following what is described in `postgres_init_gRPC_status.bash`. Additionally, a kafka broker needs to be instantiated with a topic named `Harvester`.

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
