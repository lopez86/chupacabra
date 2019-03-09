#!/bin/bash

python -m grpc_tools.protoc -I. --python_out=chupacabra_client/protos \
       --grpc_python_out=chupacabra_client/protos chupacabra_client/protos/game_structs.proto

python -m grpc_tools.protoc -I. --python_out=chupacabra_client/protos \
       --grpc_python_out=chupacabra_client/protos chupacabra_client/protos/chupacabra.proto

python -m grpc_tools.protoc -I. --python_out=chupacabra_server/protos \
       --grpc_python_out=chupacabra_server/protos chupacabra_server/protos/game_server.proto