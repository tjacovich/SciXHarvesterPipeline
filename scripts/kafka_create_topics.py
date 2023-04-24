from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.error import KafkaException, KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry import Schema

admin_client = AdminClient({"bootstrap.servers": "kafka:9092"})

topics = ["HarvesterInput", "HarvesterOutput"]

for topic_name in topics:
    while True:
        try:
            new_topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
            fs = admin_client.create_topics([new_topic], operation_timeout=30)
            # Wait for operation to finish.
            for t, f in fs.items():
                f.result()  # The result itself is None
        except KafkaException as e:
            kafka_error = e.args[0] # KafkaError
            if kafka_error.name() == "TOPIC_ALREADY_EXISTS" in kafka_error.str():
                continue
            else:
                print("Failed to create topic {}: {}".format(topic_name, e))
                print(kafka_error)
        else:
            print("Topic {} created".format(topic_name))
        break


#--------------------------------------------------------------------------------
# Registry - AVRO
#--------------------------------------------------------------------------------
sr_client = SchemaRegistryClient({'url': 'http://schema-registry:8081'})

VALUE_SCHEMA_FILE = "AVRO_schemas/HarvesterInputSchema.avsc"
VALUE_SCHEMA_NAME = "HarvesterInputSchema"
value_schema = open(VALUE_SCHEMA_FILE).read()

if VALUE_SCHEMA_NAME not in sr_client.get_subjects():
    schema_id = sr_client.register_schema(VALUE_SCHEMA_NAME, Schema(value_schema, "AVRO"))
    print("Schema '{}' registered".format(VALUE_SCHEMA_NAME))

VALUE_SCHEMA_FILE = "AVRO_schemas/HarvesterOutputSchema.avsc"
VALUE_SCHEMA_NAME = "HarvesterOutputSchema"
value_schema = open(VALUE_SCHEMA_FILE).read()

if VALUE_SCHEMA_NAME not in sr_client.get_subjects():
    schema_id = sr_client.register_schema(VALUE_SCHEMA_NAME, Schema(value_schema, "AVRO"))
    print("Schema '{}' registered".format(VALUE_SCHEMA_NAME))

