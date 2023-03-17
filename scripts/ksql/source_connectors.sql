------ Create source connectors
---- OPTION 1: Using ksql
CREATE SOURCE CONNECTOR IF NOT EXISTS datalake_db WITH (
    'slot.name' = 'debezium_datalake_db',
    'connector.class' = 'io.debezium.connector.postgresql.PostgresConnector',
    'plugin.name' = 'pgoutput',
    'database.hostname' = 'postgres',
    'database.port' = '5432',
    'database.user' = 'postgres',
    'database.password' = 'root',
    'database.dbname'  = 'datalake_db',
    'database.server.name' = 'postgres',
    'output.data.format' = 'AVRO',
    'transforms' = 'unwrap',
    'transforms.unwrap.type' = 'io.debezium.transforms.ExtractNewRecordState'
);

---- OPTION 2: Using a curl command against the connect component
-- curl -H 'Content-Type: application/json' localhost:8083/connectors --data '
-- {
  -- "name": "datalake_db-connector",  
  -- "config": {
    -- "slot.name": "debezium_datalake_db",
    -- "connector.class": "io.debezium.connector.postgresql.PostgresConnector", 
    -- "plugin.name": "pgoutput",
    -- "database.hostname": "postgres", 
    -- "database.port": "5432", 
    -- "database.user": "postgres", 
    -- "database.password": "root", 
    -- "database.dbname" : "datalake_db", 
    -- "database.server.name": "postgres", 
    -- "output.data.format": "AVRO",
    -- "transforms": "unwrap",
    -- "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState"
  -- }
-- }'
