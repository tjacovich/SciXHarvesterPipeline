-- When consuming from Kafka read all existing messages too
SET 'auto.offset.reset' = 'earliest';

CREATE STREAM IF NOT EXISTS admission_src WITH (KAFKA_TOPIC='postgres.public.admission', VALUE_FORMAT='AVRO');
CREATE STREAM IF NOT EXISTS admission_src_rekey WITH (PARTITIONS=1) AS SELECT * FROM admission_src PARTITION BY student_id;

CREATE STREAM IF NOT EXISTS research_src WITH (KAFKA_TOPIC='postgres.public.research', VALUE_FORMAT='AVRO');
CREATE STREAM IF NOT EXISTS research_src_rekey WITH (PARTITIONS=1) AS SELECT * FROM research_src PARTITION BY student_id;

------ Postgres Sink Test
------ Inspiration: https://rmoff.net/2021/03/12/kafka-connect-jdbc-sink-deep-dive-working-with-primary-keys/

---- OPTION 1: Null keys + structured value
---- * It does not allow deletion from Postgres table

CREATE STREAM IF NOT EXISTS TEST_SINK_01 (IDENTIFIER INT, PASSPORT VARCHAR, YEAR INT, ZIP INT, CITY VARCHAR)
  WITH (KAFKA_TOPIC='TEST_SINK_01', VALUE_FORMAT='AVRO', PARTITIONS=1);


-- OPTION 2: String key + structured value

CREATE STREAM IF NOT EXISTS TEST_SINK_02 (IDENTIFIER INT KEY, PASSPORT VARCHAR, YEAR INT, ZIP INT, CITY VARCHAR)
  WITH (KAFKA_TOPIC='TEST_SINK_02', KEY_FORMAT='KAFKA', VALUE_FORMAT='AVRO', PARTITIONS=1);

-- OPTION 3: Structure key + structured value

CREATE STREAM IF NOT EXISTS TEST_SINK_03 (IDENTIFIER INT KEY, PASSPORT VARCHAR KEY, YEAR INT, ZIP INT, CITY VARCHAR)
  WITH (KAFKA_TOPIC='TEST_SINK_03', KEY_FORMAT='AVRO', VALUE_FORMAT='AVRO', PARTITIONS=1);

-- 
UNSET 'auto.offset.reset';
