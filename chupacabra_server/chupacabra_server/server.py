#!/usr/bin/env python
from concurrent.futures import ThreadPoolExecutor
import logging
import time

from chupacabra_client.protos.chupacabra_pb2_grpc import (
    ChupacabraServerServicer, add_ChupacabraServerServicer_to_server
)
import click
import grpc

from protos.game_server_pb2_grpc import GameServerStub


logger = logging.getLogger(__name__)


ONE_DAY = 24 * 60 * 60


@click.command()
@click.option('--host', default='127.0.0.1', help='Host address')
@click.option('--port', default=7653, help='Port number to expose')
@click.option('--max_workers', default=10, help='Maximum number of worker threads.')
def serve(host: str, port: int, max_workers: int) -> None:
    """Create and run a Tic Tac Toe server"""
    logger.info('Starting Chupacabra server')
    executor = ThreadPoolExecutor(max_workers=max_workers)
    server = grpc.server(executor)

    implementation = make_chupacabra_implementation()
    servicer = ChupacabraServerServicer(implementation)

    add_ChupacabraServerServicer_to_server(servicer, server)
    server.add_insecure_port('{}:{}'.format(host, port))
    server.start()
    logger.info('Server now running at {}:{}'.format(host, port))
    # Nothing is blocking this from ending, so we need an infinite sleep loop
    while True:
        time.sleep(ONE_DAY)


if __name__ == '__main__':
    serve()
