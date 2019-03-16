#!/usr/bin/env python
from concurrent.futures import ThreadPoolExecutor
import time

import click
import grpc

from game_server.game_servicer import BasicGameServicer
from protos import game_server_pb2_grpc
from tic_tac_toe.game_implementation import make_tic_tac_toe_implementation


ONE_DAY = 24 * 60 * 60  # in seconds


@click.command()
@click.option('--host', default='127.0.0.1', guidance='Host address')
@click.option('--port', default=7654, guidance='Port number to expose')
@click.option('--max_workers', default=10, guidance='Maximum number of worker threads.')
def serve(host: str, port: int, max_workers: int) -> None:
    """Create and run a Tic Tac Toe server"""
    executor = ThreadPoolExecutor(max_workers=max_workers)
    server = grpc.server(executor)

    implementation = make_tic_tac_toe_implementation()
    servicer = BasicGameServicer(implementation)

    game_server_pb2_grpc.add_GameServerServicer_to_server(servicer, server)
    server.add_insecure_port('{}:{}'.format(host, port))
    server.start()

    # Nothing is blocking this from ending, so we need an infinite sleep loop
    while True:
        time.sleep(ONE_DAY)


if __name__ == '__main__':
    serve()
