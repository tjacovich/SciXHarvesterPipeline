from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro import AvroProducer
from confluent_kafka.schema_registry import SchemaRegistryClient

from datetime import datetime
import time
import random
import logging
import json
import os
import json
import sys
import redis
import boto3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from arxiv_harvester import arxiv_harvesting
import s3_methods as s3

sys.path.append("/app/")

import harvester.db as db

proj_home = os.path.realpath('../')
config = db.load_config(proj_home=proj_home)

def _consume_from_topic(consumer):
    logger.debug("Consuming from Harvester Topic")
    return consumer.poll()

class Harvester_APP:
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def __init__(self):
        self.engine = create_engine(config.get('SQLALCHEMY_URL'))
        self.s3_methods = s3(boto3.client('s3'))
        self.Session = sessionmaker(self.engine)
        self.redis = redis.StrictRedis(config.get('REDIS_HOST', 'localhost'), config.get('REDIS_PORT', 6379), charset="utf-8", decode_responses=True) 
    

def Harvester_task(consumer):
    while True:
        msg = _consume_from_topic(consumer)
        if msg:
            Finish = False
            tstamp = datetime.now()
            logger.debug("Received message {}".format(msg.value()))
            job_request = msg.value()
            job_request["status"] = "Processing"
            db.update_job_status(app, job_request["hash"], job_request["status"])
            db.write_status_redis(app.redis, json.dumps({"job_id":job_request["hash"], "status":job_request["status"]}))
            logger.debug(b'This message was generated by the Harvester and was read from the gRPC topic %s.' % bytes(str(tstamp), 'utf-8'))
            
            if job_request.get("task") == "ARXIV":
                arxiv_harvesting(app, job_request, producer)

            job_request["status"] = 'Success'
            db.update_job_status(app, job_request["hash"], status = job_request["status"])
            db.write_status_redis(app.redis, json.dumps({"job_id":job_request["hash"], "status":job_request["status"]}))
            tstamp = datetime.now()            
            logger.info(b'Done %s.' % bytes(str(tstamp), 'utf-8'))

        else:
            logger.debug("No new messages")
            time.sleep(2)
            continue

def _get_schema(schema_client):          
    try:
        avro_schema = schema_client.get_schema(config.get("SCHEMA_ID"))
        logger.info("Found schema: {}".format(avro_schema.schema_str))
    except Exception as e:
        avro_schema = None
        logger.warning("Could not retrieve avro schema with exception: {}".format(e))

    return avro_schema.schema_str

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger=logging.getLogger(__name__)
    logger.info("Starting Harvester Service")
    logger.info(config)
    schema_client = SchemaRegistryClient({'url': config.get("SCHEMA_REGISTRY_URL")})
    schema = _get_schema(schema_client)
    consumer = AvroConsumer({'bootstrap.servers': config.get("KAFKA_BROKER"), 'schema.registry.url': config.get("SCHEMA_REGISTRY_URL"), 'auto.offset.reset': 'latest', 'group.id': 'HarvesterPipeline1'}, reader_value_schema = schema)
    consumer.subscribe(['Harvester'])
    producer = AvroProducer({'bootstrap.servers': config.get("KAFKA_BROKER"), 'schema.registry.url': config.get("SCHEMA_REGISTRY_URL")})
    app = Harvester_APP()
    Harvester_task(consumer)

