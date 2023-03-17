To install gRPC, the following variable may need to be set in order for the build to succeed:

```
export GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1
export GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1
```

It's also important for `wheel` to be installed.

Requests can be initiated using:
```
gRPCHarvester/harvester_client.py HARVESTER_INIT --task "ARXIV" --task_args '{"ingest": "True", "ingest_type": "thumbnails"}'
```

This will return a dictionary that contains a `job_id`.

The status of the job can be check using
```
python3 harvester_gRPC/gRPCHarvester/harvester_client.py HARVESTER_MONITOR --job_id '<job_id>'
```

The flag `--persistence` can be added to either command to open a continuous connection to the server where updates are streamed as they become available.