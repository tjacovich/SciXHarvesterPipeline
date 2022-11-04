Test Harvester repository

## Setting Up a Development Environment.
Running `docker-compose up --build -d --force-recreate` will stand up a docker container with supervised instances of the harvester mock pipeline and the gRPC server. For full functionality, a postgres database needs to be setup and provisioned following what is described in `postgres_init_gRPC_status.bash`. Additionally, a kafka broker needs to be instantiated with a topic named `Harvester`.

## Sending commands to the gRPC API

Currently, there are two methods that have been defined in the API for interacting with the Harvester Pipeline. 
- `HARVESTER_INIT`: Initialize a job with given `job_args` passed into the script as a JSON.
- `HARVESTER_MONITOR`: Queries the status of a job with a given `<job_id>`

currently, the only argument that can be passed with job_args is `"persistence"`, which is a boolean that tells the server whether to keep the connection open and stream updates to the client.

```bash
#This command tells the server to initialize a job by adding a message to the Harvester Topic
python3 harvester_gRPC/gRPCHarvester/harvester_client.py HARVESTER_INIT
#This command asks the server to check on the current status of a job with <job_id>
python3 harvester_gRPC/gRPCHarvester/harvester_client.py HARVESTER_MONITOR '<job_id>`
```