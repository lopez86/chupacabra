#!/bin/bash

python -m grpc_tools.protoc -I. --python_out=. \
       --grpc_python_out=. chupacabra_client/protos/game_structs.proto

python -m grpc_tools.protoc -I. --python_out=. \
       --grpc_python_out=. chupacabra_client/protos/chupacabra.proto

CWD=$PWD
cd chupacabra_server
python -m grpc_tools.protoc -I. -I.. --python_out=. \
       --grpc_python_out=. protos/game_server.proto
cd $CWD
