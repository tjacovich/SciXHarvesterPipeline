------ Postgres Sink Test
------ Inspiration: https://rmoff.net/2021/03/12/kafka-connect-jdbc-sink-deep-dive-working-with-primary-keys/

---- OPTION 1: Null keys + structured value
---- * It does not allow deletion from Postgres table

INSERT INTO TEST_SINK_01 (IDENTIFIER, PASSPORT, YEAR, ZIP, CITY) VALUES (0, 'X4283P', 2000, 43005, 'Tarragona');
INSERT INTO TEST_SINK_01 (IDENTIFIER, PASSPORT, YEAR, ZIP, CITY) VALUES (1, '00X310', 2012, 08080, 'Barcelona');
INSERT INTO TEST_SINK_01 (IDENTIFIER, PASSPORT, YEAR, ZIP, CITY) VALUES (1, '00X310', 2022, 02138, 'Cambridge');

-- OPTION 2: String key + structured value

INSERT INTO TEST_SINK_02 (IDENTIFIER, PASSPORT, YEAR, ZIP, CITY) VALUES (0, 'X4283P', 2000, 43005, 'Tarragona');
INSERT INTO TEST_SINK_02 (IDENTIFIER, PASSPORT, YEAR, ZIP, CITY) VALUES (1, '00X310', 2012, 08080, 'Barcelona');
INSERT INTO TEST_SINK_02 (IDENTIFIER, PASSPORT, YEAR, ZIP, CITY) VALUES (1, '00X310', 2022, 02138, 'Cambridge');

-- OPTION 3: Structure key + structured value

INSERT INTO TEST_SINK_03 (IDENTIFIER, PASSPORT, YEAR, ZIP, CITY) VALUES (0, 'X4283P', 2000, 43005, 'Tarragona');
INSERT INTO TEST_SINK_03 (IDENTIFIER, PASSPORT, YEAR, ZIP, CITY) VALUES (1, '00X310', 2012, 08080, 'Barcelona');
INSERT INTO TEST_SINK_03 (IDENTIFIER, PASSPORT, YEAR, ZIP, CITY) VALUES (1, '00X310', 2022, 02138, 'Cambridge');

---- Send a null value with key 0 to produce a deletion in the postgres table
-- echo "0:" | docker run --rm --network kafka --platform linux/amd64 confluentinc/cp-kafkacat kafkacat -b kafka:9092 -t TEST_SINK_03 -Z -K: -P

-- PRINT TEST_SINK_01 FROM BEGINNING LIMIT 1;
-- PRINT TEST_SINK_02 FROM BEGINNING LIMIT 1;
-- PRINT TEST_SINK_03 FROM BEGINNING LIMIT 1;

