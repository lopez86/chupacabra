from chupacabra_client.protos import chupacabra_pb2
from chupacabra_client.protos.chupacabra_pb2_grpc import ChupacabraServerStub
import click
import flask
from google.protobuf import json_format
import grpc


def make_grpc_stub(url: str, port: int) -> ChupacabraServerStub:
    """Make a stub for the GRPC server."""
    location = '{}:{}'.format(url, port)
    channel = grpc.insecure_channel(location)
    stub = ChupacabraServerStub(channel)
    return stub


def create_app(grpc_host: str, grpc_port: int) -> flask.Flask:
    """Create a flask app with bindings for the various endpoints."""
    app = flask.Flask('ChupacabraFlask')

    stub = make_grpc_stub(grpc_host, grpc_port)

    @app.route('/RegisterUser', methods=('POST',))
    def register_user():
        print('Got request')
        json_data = flask.request.get_json()
        grpc_request = json_format.Parse(
            json_data,
            chupacabra_pb2.UserRequest()
        )
        response = stub.RegisterUser(grpc_request)
        json_output = json_format.MessageToJson(response)
        print('Outputting: ')
        print(json_output)
        return json_output

    @app.route('/BeginSession', methods=('POST',))
    def begin_session():

        json_data = flask.request.get_json()
        grpc_request = json_format.Parse(
            json_data,
            chupacabra_pb2.SessionRequest()
        )
        response = stub.BeginSession(grpc_request)
        json_output = json_format.MessageToJson(response)
        return json_output

    @app.route('/ListAvailableGames', methods=('POST',))
    def list_available_games():
        json_data =flask.request.get_json()
        grpc_request = json_format.Parse(
            json_data,
            chupacabra_pb2.PlayerGameInfo()
        )
        response = stub.ListAvailableGames(grpc_request)
        json_output = json_format.MessageToJson(response)
        return json_output

    @app.route('/RequestGame', methods=('POST',))
    def request_game():
        json_data = flask.request.get_json()
        grpc_request = json_format.Parse(
            json_data,
            chupacabra_pb2.GameRequest()
        )
        response = stub.RequestGame(grpc_request)
        json_output = json_format.MessageToJson(response)
        return json_output

    @app.route('/CheckGameRequest', methods=('POST',))
    def check_game_request():
        json_data = flask.request.get_json()
        grpc_request = json_format.Parse(
            json_data,
            chupacabra_pb2.GameRequestStatus()
        )
        response = stub.CheckGameRequest(grpc_request)
        json_output = json_format.MessageToJson(response)
        return json_output

    @app.route('/GetGameState', methods=('POST',))
    def get_game_state():
        json_data = flask.request.get_json()
        grpc_request = json_format.Parse(
            json_data,
            chupacabra_pb2.PlayerGameInfo()
        )
        response = stub.GetGameState(grpc_request)
        json_output = json_format.MessageToJson(response)
        return json_output

    @app.route('/CheckLegalMoves', methods=('POST',))
    def check_legal_moves():
        json_data = flask.request.get_json()
        grpc_request = json_format.Parse(
            json_data,
            chupacabra_pb2.PlayerGameInfo()
        )
        response = stub.CheckLegalMoves(grpc_request)
        json_output = json_format.MessageToJson(response)
        return json_output

    @app.route('/MakeMove', methods=('POST',))
    def make_move():
        json_data = flask.request.get_json()
        grpc_request = json_format.Parse(
            json_data,
            chupacabra_pb2.MoveRequest
        )
        response = stub.MakeMove(grpc_request)
        json_output = json_format.MessageToJson(response)
        return json_output

    @app.route('/ForfeitGame', methods=('POST',))
    def forfeit_game():
        json_data = flask.request.get_json()
        grpc_request = json_format.Parse(
            json_data,
            chupacabra_pb2.PlayerGameInfo()
        )
        response = stub.ForfeitGame(grpc_request)
        json_output = json_format.MessageToJson(response)
        return json_output

    return app


@click.command()
@click.option('--host', default='127.0.0.1', help='Host address')
@click.option('--port', default=7655, help='Host port')
@click.option('--grpc_host', default='localhost', help='GRPC server')
@click.option('--grpc_port', default=7653, help='Port on GRPC server')
def run_server(host: str, port: int, grpc_host: str, grpc_port: int) -> None:
    """Run a Flask server for easy http access to endpoints."""
    app = create_app(grpc_host, grpc_port)
    app.run(host=host, port=port)


# Actually run the server here.
if __name__ == '__main__':
    run_server()
