from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro import AvroProducer
from confluent_kafka.schema_registry import SchemaRegistryClient

import os

from harvester import harvester, utils


if __name__ == "__main__":
    proj_home = os.path.realpath('/app/')
    app = harvester.Harvester_APP(proj_home)
    app.schema_client = SchemaRegistryClient({'url': app.config.get("SCHEMA_REGISTRY_URL")})
    schema = utils.get_schema(app, app.schema_client, app.config.get('HARVESTER_INPUT_SCHEMA'))
    consumer = AvroConsumer({'bootstrap.servers': app.config.get("KAFKA_BROKER"), 'schema.registry.url': app.config.get("SCHEMA_REGISTRY_URL"), 'auto.offset.reset': 'latest', 'group.id': 'HarvesterPipeline1'}, reader_value_schema = schema)
    consumer.subscribe([app.config.get('HARVESTER_INPUT_TOPIC', 'Harvester')])
    producer = AvroProducer({'bootstrap.servers': app.config.get("KAFKA_BROKER"), 'schema.registry.url': app.config.get("SCHEMA_REGISTRY_URL")})
    app.logger.info("Starting Harvester APP")
    app.Harvester_task(consumer, producer)

