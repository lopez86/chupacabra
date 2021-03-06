# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: protos/game_server.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from chupacabra_client.protos import game_structs_pb2 as chupacabra__client_dot_protos_dot_game__structs__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='protos/game_server.proto',
  package='game_server',
  syntax='proto3',
  serialized_pb=_b('\n\x18protos/game_server.proto\x12\x0bgame_server\x1a\x1bgoogle/protobuf/empty.proto\x1a+chupacabra_client/protos/game_structs.proto\"O\n\x0bGameRequest\x12\x11\n\tplayer_id\x18\x01 \x01(\t\x12-\n\x0bplayer_info\x18\x02 \x01(\x0b\x32\x18.game_structs.PlayerInfo\"A\n\x18GameRequestStatusRequest\x12\x11\n\tplayer_id\x18\x01 \x01(\t\x12\x12\n\nrequest_id\x18\x02 \x01(\t\"2\n\x0cUserGameInfo\x12\x11\n\tplayer_id\x18\x01 \x01(\t\x12\x0f\n\x07game_id\x18\x02 \x01(\t\"]\n\x0bMoveRequest\x12,\n\tgame_info\x18\x01 \x01(\x0b\x32\x19.game_server.UserGameInfo\x12 \n\x04move\x18\x02 \x01(\x0b\x32\x12.game_structs.Move2\x8d\x05\n\nGameServer\x12L\n\x0bRequestGame\x12\x18.game_server.GameRequest\x1a!.game_structs.GameRequestResponse\"\x00\x12\x64\n\x10\x43heckGameRequest\x12%.game_server.GameRequestStatusRequest\x1a\'.game_structs.GameRequestStatusResponse\"\x00\x12G\n\x0c\x44\x65scribeGame\x12\x16.google.protobuf.Empty\x1a\x1d.game_structs.GameDescription\"\x00\x12J\n\rDescribeMoves\x12\x16.google.protobuf.Empty\x1a\x1f.game_structs.GameMovesResponse\"\x00\x12H\n\x08MakeMove\x12\x18.game_server.MoveRequest\x1a .game_structs.GameStatusResponse\"\x00\x12N\n\rGetGameStatus\x12\x19.game_server.UserGameInfo\x1a .game_structs.GameStatusResponse\"\x00\x12N\n\rGetLegalMoves\x12\x19.game_server.UserGameInfo\x1a .game_structs.LegalMovesResponse\"\x00\x12L\n\x0b\x46orfeitGame\x12\x19.game_server.UserGameInfo\x1a .game_structs.GameStatusResponse\"\x00\x62\x06proto3')
  ,
  dependencies=[google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,chupacabra__client_dot_protos_dot_game__structs__pb2.DESCRIPTOR,])




_GAMEREQUEST = _descriptor.Descriptor(
  name='GameRequest',
  full_name='game_server.GameRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='player_id', full_name='game_server.GameRequest.player_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='player_info', full_name='game_server.GameRequest.player_info', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=115,
  serialized_end=194,
)


_GAMEREQUESTSTATUSREQUEST = _descriptor.Descriptor(
  name='GameRequestStatusRequest',
  full_name='game_server.GameRequestStatusRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='player_id', full_name='game_server.GameRequestStatusRequest.player_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='request_id', full_name='game_server.GameRequestStatusRequest.request_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=196,
  serialized_end=261,
)


_USERGAMEINFO = _descriptor.Descriptor(
  name='UserGameInfo',
  full_name='game_server.UserGameInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='player_id', full_name='game_server.UserGameInfo.player_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='game_id', full_name='game_server.UserGameInfo.game_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=263,
  serialized_end=313,
)


_MOVEREQUEST = _descriptor.Descriptor(
  name='MoveRequest',
  full_name='game_server.MoveRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='game_info', full_name='game_server.MoveRequest.game_info', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='move', full_name='game_server.MoveRequest.move', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=315,
  serialized_end=408,
)

_GAMEREQUEST.fields_by_name['player_info'].message_type = chupacabra__client_dot_protos_dot_game__structs__pb2._PLAYERINFO
_MOVEREQUEST.fields_by_name['game_info'].message_type = _USERGAMEINFO
_MOVEREQUEST.fields_by_name['move'].message_type = chupacabra__client_dot_protos_dot_game__structs__pb2._MOVE
DESCRIPTOR.message_types_by_name['GameRequest'] = _GAMEREQUEST
DESCRIPTOR.message_types_by_name['GameRequestStatusRequest'] = _GAMEREQUESTSTATUSREQUEST
DESCRIPTOR.message_types_by_name['UserGameInfo'] = _USERGAMEINFO
DESCRIPTOR.message_types_by_name['MoveRequest'] = _MOVEREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

GameRequest = _reflection.GeneratedProtocolMessageType('GameRequest', (_message.Message,), dict(
  DESCRIPTOR = _GAMEREQUEST,
  __module__ = 'protos.game_server_pb2'
  # @@protoc_insertion_point(class_scope:game_server.GameRequest)
  ))
_sym_db.RegisterMessage(GameRequest)

GameRequestStatusRequest = _reflection.GeneratedProtocolMessageType('GameRequestStatusRequest', (_message.Message,), dict(
  DESCRIPTOR = _GAMEREQUESTSTATUSREQUEST,
  __module__ = 'protos.game_server_pb2'
  # @@protoc_insertion_point(class_scope:game_server.GameRequestStatusRequest)
  ))
_sym_db.RegisterMessage(GameRequestStatusRequest)

UserGameInfo = _reflection.GeneratedProtocolMessageType('UserGameInfo', (_message.Message,), dict(
  DESCRIPTOR = _USERGAMEINFO,
  __module__ = 'protos.game_server_pb2'
  # @@protoc_insertion_point(class_scope:game_server.UserGameInfo)
  ))
_sym_db.RegisterMessage(UserGameInfo)

MoveRequest = _reflection.GeneratedProtocolMessageType('MoveRequest', (_message.Message,), dict(
  DESCRIPTOR = _MOVEREQUEST,
  __module__ = 'protos.game_server_pb2'
  # @@protoc_insertion_point(class_scope:game_server.MoveRequest)
  ))
_sym_db.RegisterMessage(MoveRequest)



_GAMESERVER = _descriptor.ServiceDescriptor(
  name='GameServer',
  full_name='game_server.GameServer',
  file=DESCRIPTOR,
  index=0,
  options=None,
  serialized_start=411,
  serialized_end=1064,
  methods=[
  _descriptor.MethodDescriptor(
    name='RequestGame',
    full_name='game_server.GameServer.RequestGame',
    index=0,
    containing_service=None,
    input_type=_GAMEREQUEST,
    output_type=chupacabra__client_dot_protos_dot_game__structs__pb2._GAMEREQUESTRESPONSE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='CheckGameRequest',
    full_name='game_server.GameServer.CheckGameRequest',
    index=1,
    containing_service=None,
    input_type=_GAMEREQUESTSTATUSREQUEST,
    output_type=chupacabra__client_dot_protos_dot_game__structs__pb2._GAMEREQUESTSTATUSRESPONSE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='DescribeGame',
    full_name='game_server.GameServer.DescribeGame',
    index=2,
    containing_service=None,
    input_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    output_type=chupacabra__client_dot_protos_dot_game__structs__pb2._GAMEDESCRIPTION,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='DescribeMoves',
    full_name='game_server.GameServer.DescribeMoves',
    index=3,
    containing_service=None,
    input_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
    output_type=chupacabra__client_dot_protos_dot_game__structs__pb2._GAMEMOVESRESPONSE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='MakeMove',
    full_name='game_server.GameServer.MakeMove',
    index=4,
    containing_service=None,
    input_type=_MOVEREQUEST,
    output_type=chupacabra__client_dot_protos_dot_game__structs__pb2._GAMESTATUSRESPONSE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='GetGameStatus',
    full_name='game_server.GameServer.GetGameStatus',
    index=5,
    containing_service=None,
    input_type=_USERGAMEINFO,
    output_type=chupacabra__client_dot_protos_dot_game__structs__pb2._GAMESTATUSRESPONSE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='GetLegalMoves',
    full_name='game_server.GameServer.GetLegalMoves',
    index=6,
    containing_service=None,
    input_type=_USERGAMEINFO,
    output_type=chupacabra__client_dot_protos_dot_game__structs__pb2._LEGALMOVESRESPONSE,
    options=None,
  ),
  _descriptor.MethodDescriptor(
    name='ForfeitGame',
    full_name='game_server.GameServer.ForfeitGame',
    index=7,
    containing_service=None,
    input_type=_USERGAMEINFO,
    output_type=chupacabra__client_dot_protos_dot_game__structs__pb2._GAMESTATUSRESPONSE,
    options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_GAMESERVER)

DESCRIPTOR.services_by_name['GameServer'] = _GAMESERVER

# @@protoc_insertion_point(module_scope)
