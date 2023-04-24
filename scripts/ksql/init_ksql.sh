#!/bin/bash
set -e
set -x
docker run -it --rm --network kafka --volume ${PWD}/scripts/ksql/source_connectors.sql:/tmp/source_connectors.sql --platform linux/amd64 confluentinc/ksqldb-cli ksql --file /tmp/source_connectors.sql -- http://ksql:8088
docker run -it --rm --network kafka --volume ${PWD}/scripts/ksql/streams.sql:/tmp/streams.sql --platform linux/amd64 confluentinc/ksqldb-cli ksql --file /tmp/streams.sql -- http://ksql:8088
docker run -it --rm --network kafka --volume ${PWD}/scripts/ksql/tables.sql:/tmp/tables.sql --platform linux/amd64 confluentinc/ksqldb-cli ksql --file /tmp/tables.sql -- http://ksql:8088
docker run -it --rm --network kafka --volume ${PWD}/scripts/ksql/sink_connectors.sql:/tmp/sink_connectors.sql --platform linux/amd64 confluentinc/ksqldb-cli ksql --file /tmp/sink_connectors.sql -- http://ksql:8088
docker run -it --rm --network kafka --volume ${PWD}/scripts/ksql/inserts.sql:/tmp/inserts.sql --platform linux/amd64 confluentinc/ksqldb-cli ksql --file /tmp/inserts.sql -- http://ksql:8088
