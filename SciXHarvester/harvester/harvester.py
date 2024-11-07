import json
import logging
import time
from contextlib import contextmanager
from datetime import datetime

import redis
from confluent_kafka.avro import AvroConsumer, AvroProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.confluent_kafka import ConfluentKafkaInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from SciXPipelineUtils import utils
from SciXPipelineUtils.s3_methods import load_s3_providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import harvester.metadata.arxiv_harvester as arxiv_harvester
from harvester import db


def init_pipeline(proj_home):
    app = Harvester_APP(proj_home)
    resource = Resource(attributes={"service.name": "harvester"})
    # Initiate OpenTelemetry span exporter
    trace.set_tracer_provider(TracerProvider(resource=resource))
    # create a JaegerSpanExporter
    jaeger_exporter = OTLPSpanExporter()
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    console_exporter = ConsoleSpanExporter()
    console_span_processor = SimpleSpanProcessor(console_exporter)
    trace.get_tracer_provider().add_span_processor(console_span_processor)
    ConfluentKafkaInstrumentor().instrument()

    app.schema_client = SchemaRegistryClient({"url": app.config.get("SCHEMA_REGISTRY_URL")})
    schema = utils.get_schema(app, app.schema_client, app.config.get("HARVESTER_INPUT_SCHEMA"))
    consumer = AvroConsumer(
        {
            "bootstrap.servers": app.config.get("KAFKA_BROKER"),
            "schema.registry.url": app.config.get("SCHEMA_REGISTRY_URL"),
            "auto.offset.reset": "latest",
            "group.id": "HarvesterPipeline1",
        },
        reader_value_schema=schema,
    )
    consumer.subscribe([app.config.get("HARVESTER_INPUT_TOPIC", "Harvester")])
    producer = AvroProducer(
        {
            "bootstrap.servers": app.config.get("KAFKA_BROKER"),
            "schema.registry.url": app.config.get("SCHEMA_REGISTRY_URL"),
            "auto.register.schemas": False,
        }
    )
    app.logger.info("Starting Harvester APP")
    app.harvester_consumer(consumer, producer)


class Harvester_APP:
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _consume_from_topic(self, consumer):
        self.logger.debug("Consuming from Harvester Topic")
        return consumer.poll()

    def _init_logger(self):
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Starting Harvester Service Logging")

    def __init__(self, proj_home):
        self.config = utils.load_config(proj_home)
        self.engine = create_engine(self.config.get("SQLALCHEMY_URL"))
        self.logger = None
        self.schema_client = None
        self._init_logger()
        self.s3Clients = load_s3_providers(self.config)
        self.Session = sessionmaker(self.engine)
        self.redis = redis.StrictRedis(
            self.config.get("REDIS_HOST", "localhost"),
            self.config.get("REDIS_PORT", 6379),
            decode_responses=True,
        )

    def harvester_consumer(self, consumer, producer):
        while True:
            msg = self._consume_from_topic(consumer)
            if msg:
                self.harvester_task(msg, producer)
            else:
                self.logger.debug("No new messages")
                time.sleep(2)
                continue

    def harvester_task(self, msg, producer):
        tstamp = datetime.now()
        self.logger.debug("Received message {}".format(msg.value()))
        job_request = msg.value()
        task_args = job_request.get("task_args")
        job_request["status"] = "Processing"
        db.update_job_status(self, job_request["hash"], job_request["status"])
        db.write_status_redis(
            self.redis,
            json.dumps({"job_id": job_request["hash"], "status": job_request["status"]}),
        )

        if job_request.get("task") == "ARXIV":
            if task_args.get("ingest_type") == "metadata":
                job_request["status"] = arxiv_harvester.arxiv_harvesting(
                    self, job_request, producer
                )
        else:
            job_request["status"] = "Error"
        db.update_job_status(self, job_request["hash"], status=job_request["status"])
        db.write_status_redis(
            self.redis,
            json.dumps({"job_id": job_request["hash"], "status": job_request["status"]}),
        )
        tstamp = datetime.now()
        self.logger.info(b"Done %s." % bytes(str(tstamp), "utf-8"))
