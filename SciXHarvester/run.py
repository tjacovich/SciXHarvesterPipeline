
from harvester import harvester
from API import harvester_server
import asyncio
import os
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='commands', dest="action")
    subparsers.add_parser('HARVESTER_API', help='Initialize Harvester gRPC API')
    subparsers.add_parser('HARVESTER_APP', help='Initialize Harvester Working Unit')
    args = parser.parse_args()
    
    if args.action == 'HARVESTER_APP':
        proj_home = os.path.realpath('/app/SciXHarvester/')
        harvester.init_pipeline(proj_home)
    
    elif args.action == 'HARVESTER_API':
        asyncio.run(harvester_server.serve())