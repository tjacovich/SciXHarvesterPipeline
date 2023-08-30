import argparse
import asyncio
import os
from multiprocessing import Process

from SciXPipelineUtils import utils

from API import harvester_server
from harvester import harvester

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="commands", dest="action")
    subparsers.add_parser("HARVESTER_API", help="Initialize Harvester gRPC API")
    subparsers.add_parser("HARVESTER_APP", help="Initialize Harvester Working Unit")
    args = parser.parse_args()

    if args.action == "HARVESTER_APP":
        path = os.path.dirname(__file__)
        proj_home = os.path.realpath(path)
        config = utils.load_config(proj_home)

        proj_home = path
        consumer_topic_name = config.get("HARVESTER_CLASSIC_TOPIC")
        consumer_schema_name = config.get("HARVESTER_CLASSIC_SCHEMA")
        Process(target=harvester.init_pipeline(proj_home), args=(proj_home, None, None)).start()
        Process(
            target=harvester.init_pipeline,
            args=(proj_home, consumer_topic_name, consumer_schema_name),
        ).start()

    elif args.action == "HARVESTER_API":
        asyncio.run(harvester_server.serve())
