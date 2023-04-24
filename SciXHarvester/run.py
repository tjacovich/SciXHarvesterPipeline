import argparse
import asyncio
import os

from API import harvester_server
from harvester import harvester

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="commands", dest="action")
    subparsers.add_parser("HARVESTER_API", help="Initialize Harvester gRPC API")
    subparsers.add_parser("HARVESTER_APP", help="Initialize Harvester Working Unit")
    args = parser.parse_args()

    if args.action == "HARVESTER_APP":
        proj_home = os.path.realpath("/app/SciXHarvester/")
        harvester.init_pipeline(proj_home)

    elif args.action == "HARVESTER_API":
        asyncio.run(harvester_server.serve())
