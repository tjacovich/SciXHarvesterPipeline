------ Create Postgres Sink Test
------ Source: https://highalpha.com/data-stream-processing-for-newbies-with-kafka-ksql-and-postgres/

---- Create source connectors
-- OPTION 1: Using ksql

CREATE SINK CONNECTOR IF NOT EXISTS RESEARCH_AVE_BOOST WITH (
    'tasks.max'                               = '1',
    'connector.class'                         = 'io.confluent.connect.jdbc.JdbcSinkConnector',
    'connection.url'                          = 'jdbc:postgresql://postgres:5432/datalake_db',
    'connection.user'                         = 'postgres',
    'connection.password'                     = 'root',
    'topics'                                  = 'RESEARCH_AVE_BOOST',
    'key.converter'                           = 'org.apache.kafka.connect.converters.IntegerConverter',
    --'key.converter'                           = 'org.apache.kafka.connect.storage.StringConverter',
    'value.converter'                         = 'io.confluent.connect.avro.AvroConverter',
    'value.converter.schemas.enable'          = 'true',
    'value.converter.schema.registry.url'     = 'http://schema-registry:8081',
    'auto.create'                             = 'true',
    'auto.evolve'                             = 'true',
    'insert.mode'                             = 'upsert',
    'pk.mode'                                 = 'record_key',
    'pk.fields'                               = 'RESEARCH',
    'delete.enabled'                          = 'true'
);

-- OPTION 2: Using a curl command against the connect component
-- curl -H 'Content-Type: application/json' localhost:8083/connectors --data '
-- {
  -- "name": "RESEARCH_AVE_BOOST",
  -- "config": {
    -- "tasks.max": "1",
    -- "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
    -- "connection.url": "jdbc:postgresql://postgres:5432/datalake_db",
    -- "connection.user": "postgres",
    -- "connection.password": "root",
    -- "topics": "RESEARCH_AVE_BOOST",
    -- "key.converter": "org.apache.kafka.connect.converters.IntegerConverter",
    -- "value.converter": "io.confluent.connect.avro.AvroConverter",
    -- "value.converter.schemas.enable": "true",
    -- "value.converter.schema.registry.url": "http://schema-registry:8081",
    -- "auto.create": "true",
    -- "auto.evolve": "true",
    -- "insert.mode": "upsert",
    -- "pk.mode": "record_key",
    -- "pk.fields": "RESEARCH",
    -- "delete.enabled": "true"
  -- }
-- }'




------ Postgres Sink Test
------ Inspiration: https://rmoff.net/2021/03/12/kafka-connect-jdbc-sink-deep-dive-working-with-primary-keys/

---- OPTION 1: Null keys + structured value
---- * It does not allow deletion from Postgres table

CREATE SINK CONNECTOR IF NOT EXISTS TEST_SINK_01 WITH (
    'tasks.max'                               = '1',
    'connector.class'                         = 'io.confluent.connect.jdbc.JdbcSinkConnector',
    'connection.url'                          = 'jdbc:postgresql://postgres:5432/datalake_db',
    'connection.user'                         = 'postgres',
    'connection.password'                     = 'root',
    'topics'                                  = 'TEST_SINK_01',
    'key.converter'                           = 'io.confluent.connect.avro.AvroConverter',
    'key.converter.schemas.enable'            = 'true',
    'key.converter.schema.registry.url'       = 'http://schema-registry:8081',
    'value.converter'                         = 'io.confluent.connect.avro.AvroConverter',
    'value.converter.schemas.enable'          = 'true',
    'value.converter.schema.registry.url'     = 'http://schema-registry:8081',
    'auto.create'                             = 'true',
    'auto.evolve'                             = 'true',
    'insert.mode'                             = 'upsert',
    'pk.mode'                                 = 'record_value',
    'pk.fields'                               = 'IDENTIFIER,PASSPORT',
    'delete.enabled'                          = 'false'
);


-- OPTION 2: String key + structured value

CREATE SINK CONNECTOR IF NOT EXISTS TEST_SINK_02 WITH (
    'tasks.max'                               = '1',
    'connector.class'                         = 'io.confluent.connect.jdbc.JdbcSinkConnector',
    'connection.url'                          = 'jdbc:postgresql://postgres:5432/datalake_db',
    'connection.user'                         = 'postgres',
    'connection.password'                     = 'root',
    'topics'                                  = 'TEST_SINK_02',
    'key.converter'                           = 'org.apache.kafka.connect.converters.IntegerConverter',
    --'key.converter'                           = 'org.apache.kafka.connect.storage.StringConverter',
    'value.converter'                         = 'io.confluent.connect.avro.AvroConverter',
    'value.converter.schemas.enable'          = 'true',
    'value.converter.schema.registry.url'     = 'http://schema-registry:8081',
    'auto.create'                             = 'true',
    'auto.evolve'                             = 'true',
    'insert.mode'                             = 'upsert',
    'pk.mode'                                 = 'record_key',
    'pk.fields'                               = 'IDENTIFIER', -- Name that will have in the postgres table
    'delete.enabled'                          = 'true'
);

-- OPTION 3: Structure key + structured value

CREATE SINK CONNECTOR IF NOT EXISTS TEST_SINK_03 WITH (
    'tasks.max'                               = '1',
    'connector.class'                         = 'io.confluent.connect.jdbc.JdbcSinkConnector',
    'connection.url'                          = 'jdbc:postgresql://postgres:5432/datalake_db',
    'connection.user'                         = 'postgres',
    'connection.password'                     = 'root',
    'topics'                                  = 'TEST_SINK_03',
    'key.converter'                           = 'io.confluent.connect.avro.AvroConverter',
    'key.converter.schemas.enable'            = 'true',
    'key.converter.schema.registry.url'       = 'http://schema-registry:8081',
    'value.converter'                         = 'io.confluent.connect.avro.AvroConverter',
    'value.converter.schemas.enable'          = 'true',
    'value.converter.schema.registry.url'     = 'http://schema-registry:8081',
    'auto.create'                             = 'true',
    'auto.evolve'                             = 'true',
    'insert.mode'                             = 'upsert',
    'pk.mode'                                 = 'record_key',
    'pk.fields'                               = '', -- List of fields from key (empty means all of them)
    'delete.enabled'                          = 'true'
);

