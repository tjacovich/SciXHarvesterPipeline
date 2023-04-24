# Copyright 2021 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python AsyncIO implementation of the GRPC Harvester server."""

import hashlib
import json
import logging as logger
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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from API.avro_serializer import AvroSerialHelper
from API.grpc_modules.harvester_grpc import (
    HarvesterInitServicer,
    add_HarvesterInitServicer_to_server,
    add_HarvesterMonitorServicer_to_server,
)
from harvester import db, utils

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
            config.get("REDIS_HOST", "locahost"),
            config.get("REDIS_PORT", 6379),
            charset="utf-8",
            decode_responses=True,
        )
        self.subscription = self.redis.pubsub()
        self.end = False

    def subscribe(self, channel_name="harvester_statuses"):
        self.subscription.subscribe(channel_name)

    def get_status_redis(self, job_id):
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
    def __init__(self, producer, schema, schema_client):
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

    def initHarvester(self, request, context: grpc.aio.ServicerContext):
        logger.info("Serving initHarvester request %s", request)
        tstamp = datetime.now().timestamp()
        print(request)
        logger.info(json.dumps(request.get("task_args")))
        logger.info(
            "Sending {} to Harvester Topic".format(
                b" %s." % json.dumps(request.get("task_args")).encode("utf-8")
            )
        )
        hash = hashlib.sha256(bytes(str(request) + str(tstamp), "utf-8")).hexdigest()
        logger.info("{}".format(hash))

        job_request = request
        persistence = job_request["task_args"].get("persistence", False)
        job_request["task_args"].pop("persistence")
        job_request["hash"] = hash

        logger.info(job_request)

        job_request["status"] = "Pending"

        self.producer.produce(topic=self.topic, value=job_request, value_schema=self.schema)

        db.write_job_status(self, job_request)

        if persistence:
            listener = Listener()
            listener.subscribe()

            msg = db.get_job_status_by_job_hash(self, [str(hash)]).name
            logger.info("HARVESTER: User requested persitent connection.")
            logger.info("HARVESTER: Latest message is: {}".format(msg))
            job_request["status"] = str(msg)
            yield job_request
            old_msg = msg
            Done = False
            while not Done:
                if msg and msg != old_msg:
                    logger.info("yielded new status: {}".format(msg))
                    job_request["status"] = str(msg)
                    yield job_request
                    old_msg = msg
                    try:
                        if msg == "Error":
                            Done = True
                            logger.debug("Error = {}".format(Done))
                            listener.end = True
                            break
                        elif msg == "Success":
                            Done = True
                            logger.debug("Done = {}".format(Done))
                            listener.end = True
                            break

                    except Exception:
                        continue
                    try:
                        msg = next(listener.get_status_redis(hash))
                        logger.debug("HARVESTER: Redis returned: {} for job_id".format(msg))
                    except Exception:
                        msg = ""
                        continue

                else:
                    try:
                        msg = next(listener.get_status_redis(hash))
                        logger.debug("HARVESTER: Redis published new status: {}".format(msg))
                    except Exception as e:
                        logger.error("failed to read message with error: {}.".format(e))
                        continue
        else:
            yield job_request

    def monitorHarvester(self, request, context: grpc.aio.ServicerContext):
        logger.info("%s", request)
        logger.info(json.dumps(request.get("task_args")))

        job_request = request
        persistence = job_request["task_args"].get("persistence", False)

        hash = request.get("hash")

        if hash:
            msg = db.get_job_status_by_job_hash(self, [str(hash)]).name
            if persistence:
                logger.info("User requested persitent connection.")
                old_msg = None
                Done = False
                while not Done:
                    if msg and msg != old_msg:
                        logger.info("yielded new message. {}".format(msg))
                        job_request["status"] = str(msg)
                        yield job_request
                        old_msg = msg
                        try:
                            if msg == "Error":
                                Done = True
                                logger.debug("Error = {}".format(Done))
                                break
                            elif msg == "Success":
                                Done = True
                                logger.debug("Done = {}".format(Done))
                                break

                        except Exception:
                            continue
                        try:
                            msg = next(self.listener.get_status_redis(hash))
                            logger.debug("{}".format(msg))
                        except Exception:
                            msg = ""
                            continue

                    else:
                        try:
                            msg = next(self.listener.get_status_redis(hash))
                            logger.debug("Redis published new status")
                        except Exception as e:
                            logger.error("failed to read message with error: {}.".format(e))
                            continue
            else:
                job_request["status"] = str(msg)
                yield job_request
        else:
            msg = "Error"
            job_request["status"] = msg
            yield job_request


async def serve() -> None:
    server = grpc.aio.server()
    app_log = Logging(logger)
    schema_client = SchemaRegistryClient({"url": config.get("SCHEMA_REGISTRY_URL")})
    schema = utils.get_schema(app_log, schema_client, config.get("HARVESTER_INPUT_SCHEMA"))
    avroserialhelper = AvroSerialHelper(schema, app_log.logger)
    producer = AvroProducer(
        {
            "schema.registry.url": config.get("SCHEMA_REGISTRY_URL"),
            "bootstrap.servers": config.get("KAFKA_BROKER"),
        }
    )

    add_HarvesterInitServicer_to_server(
        Harvester(producer, schema, schema_client), server, avroserialhelper
    )
    add_HarvesterMonitorServicer_to_server(
        Harvester(producer, schema, schema_client), server, avroserialhelper
    )
    listen_addr = "[::]:" + str(config.get("GRPC_PORT", 50051))
    server.add_insecure_port(listen_addr)

    app_log.logger.info("Starting server on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()