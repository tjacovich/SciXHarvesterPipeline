FROM confluentinc/cp-server-connect-base:7.2.1

# See https://www.confluent.io/hub/
RUN confluent-hub install --no-prompt debezium/debezium-connector-postgresql:1.9.3
RUN confluent-hub install --no-prompt debezium/debezium-connector-mysql:1.9.3
RUN confluent-hub install --no-prompt debezium/debezium-connector-mongodb:1.9.3
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-jdbc:10.5.2
RUN confluent-hub install --no-prompt neo4j/kafka-connect-neo4j:2.0.2
RUN confluent-hub install --no-prompt jcustenborder/kafka-connect-spooldir:2.0.64
RUN confluent-hub install --no-prompt jcustenborder/kafka-connect-redis:0.0.2.17
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-s3:10.1.0
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-avro-converter:7.2.1
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-protobuf-converter:7.2.1
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-json-schema-converter:7.2.1

