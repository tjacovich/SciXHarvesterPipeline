"""The Python AsyncIO implementation of the GRPC Harvester server."""

import hashlib
import json
import logging
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from threading import Thread

import grpc
import redis
from confluent_kafka.avro import AvroProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.grpc import GrpcInstrumentorClient
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from SciXPipelineUtils import utils
from SciXPipelineUtils.avro_serializer import AvroSerialHelper
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from API.grpc_modules.harvester_grpc import (
    HarvesterInitServicer,
    add_HarvesterInitServicer_to_server,
    add_HarvesterMonitorServicer_to_server,
)
from harvester import db

resource = Resource(attributes={"service.name": "harvester-API"})

trace.set_tracer_provider(TracerProvider(resource=resource))
jaeger_exporter = OTLPSpanExporter()
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

grpc_client_instrumentor = GrpcInstrumentorClient()
grpc_client_instrumentor.instrument()

HERE = Path(__file__).parent
proj_home = str(HERE / "..")
sys.path.append(proj_home)

config = utils.load_config(proj_home=proj_home)


class Logging:
    def __init__(self, logger):
        self.logger = logger


NUMBER_OF_REPLY = 10


class Listener(Thread):
    def __init__(self):
        self.redis = redis.StrictRedis(
            config.get("REDIS_HOST", "localhost"),
            config.get("REDIS_PORT", 6379),
            charset="utf-8",
            decode_responses=True,
        )
        self.subscription = self.redis.pubsub()
        self.end = False

    def subscribe(self, channel_name="harvester_statuses"):
        self.subscription.subscribe(channel_name)

    def get_status_redis(self, job_id, logger):
        status = None
        logger.debug("DB: Listening for harvester status updates")
        logger.debug(str(self.subscription.listen()))
        for message in self.subscription.listen():
            if self.end:
                logger.debug("Ending Listener thread")
                return
            logger.debug("DB: Message from redis: {}".format(message))
            if message is not None and isinstance(message, dict):
                if message.get("data") != 1:
                    logger.debug("DB: data: {}".format(message.get("data")))
                    status_dict = json.loads(message.get("data"))
                    if status_dict["job_id"] == job_id:
                        status = status_dict["status"]
                        logger.debug("DB: status: {}".format(status))
                        yield status


class Harvester(HarvesterInitServicer):
    def __init__(self, producer, schema, schema_client, logger):
        self.topic = config.get("HARVESTER_INPUT_TOPIC")
        self.timestamp = datetime.now().timestamp()
        self.producer = producer
        self.schema = schema
        self.schema_client = schema_client
        self.serializer = AvroSerializer(
            schema_registry_client=self.schema_client, schema_str=self.schema
        )
        self.engine = create_engine(config.get("SQLALCHEMY_URL"))
        self.Session = sessionmaker(self.engine)
        self.logger = logger

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

    def persistent_connection(self, job_request, listener):
        hash = job_request.get("hash")
        msg = db.get_job_status_by_job_hash(self, [str(hash)]).name
        self.logger.info("HARVESTER: User requested persitent connection.")
        self.logger.info("HARVESTER: Latest message is: {}".format(msg))
        job_request["status"] = str(msg)
        yield job_request
        if msg == "Error":
            Done = True
            self.logger.debug("Error = {}".format(Done))
            listener.end = True
        elif msg == "Success":
            Done = True
            self.logger.debug("Done = {}".format(Done))
            listener.end = True
        else:
            Done = False
        old_msg = msg
        while not Done:
            if msg and msg != old_msg:
                self.logger.info("yielded new status: {}".format(msg))
                job_request["status"] = str(msg)
                yield job_request
                old_msg = msg
                try:
                    if msg == "Error":
                        Done = True
                        self.logger.debug("Error = {}".format(Done))
                        listener.end = True
                        break
                    elif msg == "Success":
                        Done = True
                        self.logger.debug("Done = {}".format(Done))
                        listener.end = True
                        break

                except Exception:
                    continue
                try:
                    msg = next(listener.get_status_redis(hash, self.logger))
                    self.logger.debug("HARVESTER: Redis returned: {} for job_id".format(msg))
                except Exception:
                    msg = ""
                    continue

            else:
                try:
                    msg = next(listener.get_status_redis(hash, self.logger))
                    self.logger.debug("HARVESTER: Redis published status: {}".format(msg))
                except Exception as e:
                    self.logger.error("failed to read message with error: {}.".format(e))
                    continue
        return

    def initHarvester(self, request, context: grpc.aio.ServicerContext):
        self.logger.info("Serving initHarvester request %s", request)
        tstamp = datetime.now().timestamp()
        self.logger.info(json.dumps(request.get("task_args")))
        self.logger.info(
            "Sending {} to Harvester Topic".format(
                b" %s." % json.dumps(request.get("task_args")).encode("utf-8")
            )
        )
        hash = hashlib.sha256(bytes(str(request) + str(tstamp), "utf-8")).hexdigest()
        self.logger.info("{}".format(hash))

        job_request = request
        persistence = job_request["task_args"].get("persistence", False)
        job_request["task_args"].pop("persistence")
        job_request["hash"] = hash

        self.logger.info(job_request)

        job_request["status"] = "Pending"

        self.producer.produce(topic=self.topic, value=job_request, value_schema=self.schema)

        db.write_job_status(self, job_request)

        yield job_request

        if persistence:
            listener = Listener()
            listener.subscribe()
            yield from self.persistent_connection(job_request, listener)

    def monitorHarvester(self, request, context: grpc.aio.ServicerContext):
        self.logger.info("%s", request)
        self.logger.info(json.dumps(request.get("task_args")))

        job_request = request
        persistence = job_request["task_args"].get("persistence", False)

        hash = request.get("hash")

        if hash:
            if persistence:
                listener = Listener()
                listener.subscribe()
                yield from self.persistent_connection(job_request, listener)
            else:
                msg = db.get_job_status_by_job_hash(self, [str(hash)]).name
                job_request["status"] = str(msg)
                yield job_request
        else:
            msg = "Error"
            job_request["status"] = msg
            yield job_request


async def serve() -> None:
    server = grpc.aio.server()
    app_log = Logging(logging)
    schema_client = SchemaRegistryClient({"url": config.get("SCHEMA_REGISTRY_URL")})
    schema = utils.get_schema(app_log, schema_client, config.get("HARVESTER_INPUT_SCHEMA"))
    avroserialhelper = AvroSerialHelper(schema, logger=app_log.logger)
    producer = AvroProducer(
        {
            "schema.registry.url": config.get("SCHEMA_REGISTRY_URL"),
            "bootstrap.servers": config.get("KAFKA_BROKER"),
        }
    )

    add_HarvesterInitServicer_to_server(
        Harvester(producer, schema, schema_client, app_log.logger), server, avroserialhelper
    )
    add_HarvesterMonitorServicer_to_server(
        Harvester(producer, schema, schema_client, app_log.logger), server, avroserialhelper
    )
    listen_addr = "[::]:" + str(config.get("GRPC_PORT", 50051))
    server.add_insecure_port(listen_addr)

    app_log.logger.info("Starting server on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()
