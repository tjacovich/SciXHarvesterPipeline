#!/bin/bash
#docker stop postgres
#docker rm postgres
#docker run -d -e POSTGRES_USER="root" -e POSTGRES_PASSWORD="root" -p 5432:5432 --name postgres  postgres:12.6 #http://localhost:15672
#sleep 30 
docker exec -it postgres bash -c "psql -c \"CREATE ROLE grpc_status WITH LOGIN PASSWORD 'gRPC_status';\""
docker exec -it postgres bash -c "psql -c \"CREATE DATABASE grpc_status;\""
docker exec -it postgres bash -c "psql -c \"GRANT CREATE ON DATABASE grpc_status TO gRPC_status;\""
docker exec -it postgres bash -c "psql -c \"GRANT CREATE ON DATABASE grpc_status TO gRPC_status;\""
alembic upgrade head
