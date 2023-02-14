from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro import AvroProducer
from confluent_kafka.schema_registry import SchemaRegistryClient

import os
import sys

sys.path.append("/app/")

from harvester import harvester, utils

proj_home = os.path.realpath('/app/')
config = utils.load_config(proj_home=proj_home)

if __name__ == "__main__":
    app = harvester.Harvester_APP(config)
    schema_client = SchemaRegistryClient({'url': config.get("SCHEMA_REGISTRY_URL")})
    schema = app._get_schema(schema_client)
    consumer = AvroConsumer({'bootstrap.servers': config.get("KAFKA_BROKER"), 'schema.registry.url': config.get("SCHEMA_REGISTRY_URL"), 'auto.offset.reset': 'latest', 'group.id': 'HarvesterPipeline1'}, reader_value_schema = schema)
    consumer.subscribe(config.get('HARVESTER_INPUT_TOPIC', 'Harvester'))
    producer = AvroProducer({'bootstrap.servers': config.get("KAFKA_BROKER"), 'schema.registry.url': config.get("SCHEMA_REGISTRY_URL")})
    app.logger.info("Starting Harvester APP")
    app.Harvester_task(consumer, producer)

