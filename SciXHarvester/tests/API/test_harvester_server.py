# import pytest
# import avro
# from unittest import TestCase
# from harvester_gRPC.gRPCHarvester.avro_serializer import AvroSerialHelper
# import harvester_gRPC.gRPCHarvester.grpc_modules.harvester_grpc as harvester_grpc

# @pytest.fixture(scope='module', params=[AvroSerialHelper(open("AVRO_schemas/HarvesterInputSchema.avsc", "r").read())])
# def grpc_server(_grpc_server, grpc_addr, grpc_add_to_server, grpc_servicer, request):
#     grpc_add_to_server(grpc_servicer, _grpc_server, request.param)
#     _grpc_server.add_insecure_port(grpc_addr)
#     _grpc_server.start()
#     yield _grpc_server
#     _grpc_server.stop(grace=None)

# @pytest.fixture(scope='module', params=[AvroSerialHelper(open("AVRO_schemas/HarvesterInputSchema.avsc", "r").read())])
# def grpc_stub(grpc_stub_cls, grpc_channel, request):
#     return grpc_stub_cls(grpc_channel, request.param)

# @pytest.fixture(scope='module')
# def grpc_add_to_server(request):
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

# @pytest.mark.usefixtures("grpc_add_to_server", "grpc_servicer", "grpc_stub_cls")
# def test_server_initialization(grpc_stub):
#     request = harvester_grpc.HarvesterInit()
#     response = grpc_stub.initHarvester(request)

#     assert response.name == f'test-{request.name}'
