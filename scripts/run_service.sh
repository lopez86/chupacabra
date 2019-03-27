#!/bin/bash

PYTHONPATH=$PWD:$PWD/chupacabra_server ./chupacabra_server/tic_tac_toe/server.py --host=localhost --port=7654 &
PYTHONPATH=$PWD:$PWD/chupacabra_server ./chupacabra_server/chupacabra_server/server.py --host=localhost --port=7653 --game-name=tic_tac_toe --game-server=127.0.0.1:7654

pkill -P $$
