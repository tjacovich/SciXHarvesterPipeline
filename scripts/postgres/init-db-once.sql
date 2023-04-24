CREATE ROLE harvester WITH LOGIN PASSWORD 'harvester';
GRANT CREATE ON DATABASE harvester TO harvester;