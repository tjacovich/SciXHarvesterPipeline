# import pytest

# @pytest.fixture(scope='module')
# def grpc_add_to_server():
#     from harvester_gRPC.gRPCHarvester.grpc_modules.harvester_grpc import add_HarvesterInitServicer_to_server
#     return add_HarvesterInitServicer_to_server

# @pytest.fixture(scope='module')
# def grpc_servicer():
#     from harvester_gRPC.gRPCHarvester.grpc_modules.harvester_grpc import HarvesterInitServicer

#     return HarvesterInitServicer()


# @pytest.fixture(scope='module')
# def grpc_stub_cls(grpc_channel):
#     from harvester_gRPC.gRPCHarvester.grpc_modules.harvester_grpc import HarvesterInitStub
#     return HarvesterInitStub
