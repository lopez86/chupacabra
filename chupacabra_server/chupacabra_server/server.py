#!/usr/bin/env python
from concurrent.futures import ThreadPoolExecutor
import logging
import time
from typing import List

from chupacabra_client.protos.chupacabra_pb2_grpc import add_ChupacabraServerServicer_to_server
import click
import grpc

from chupacabra_server.servicer import ChupacabraServicer


logger = logging.getLogger(__name__)


ONE_DAY = 24 * 60 * 60


@click.command()
@click.option('--host', default='127.0.0.1', help='Host address')
@click.option('--port', default=7653, help='Port number to expose')
@click.option('--max-workers', default=10, help='Maximum number of worker threads')
@click.option('--game-name', multiple=True, help='Name of a game to add to the server')
@click.option('--game-server', multiple=True, help='URL to the game server, including GRPC port')
def serve(
    host: str,
    port: int,
    max_workers: int,
    game_name: List[str],
    game_server: List[str]
) -> None:
    """Create and run a Chupacabra server"""
    logger.info('Starting Chupacabra server')
    executor = ThreadPoolExecutor(max_workers=max_workers)
    server = grpc.server(executor)

    game_dict = {
        game_name: game_server
        for game_name, game_server in zip(game_name, game_server)
    }

    servicer = ChupacabraServicer(game_dict)

    add_ChupacabraServerServicer_to_server(servicer, server)
    server.add_insecure_port('{}:{}'.format(host, port))
    server.start()
    logger.info('Server now running at {}:{}'.format(host, port))
    # Nothing is blocking this from ending, so we need an infinite sleep loop
    while True:
        time.sleep(ONE_DAY)


if __name__ == '__main__':
    serve()
