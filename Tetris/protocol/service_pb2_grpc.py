# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import HyperTexas.protocol.service_pb2 as service__pb2


class LobbyStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Handle = channel.unary_unary(
                '/lobby.Lobby/Handle',
                request_serializer=service__pb2.GeneralRequest.SerializeToString,
                response_deserializer=service__pb2.GeneralResponse.FromString,
                )
        self.Subscribe = channel.unary_stream(
                '/lobby.Lobby/Subscribe',
                request_serializer=service__pb2.GeneralRequest.SerializeToString,
                response_deserializer=service__pb2.Broadcast.FromString,
                )


class LobbyServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Handle(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Subscribe(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_LobbyServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Handle': grpc.unary_unary_rpc_method_handler(
                    servicer.Handle,
                    request_deserializer=service__pb2.GeneralRequest.FromString,
                    response_serializer=service__pb2.GeneralResponse.SerializeToString,
            ),
            'Subscribe': grpc.unary_stream_rpc_method_handler(
                    servicer.Subscribe,
                    request_deserializer=service__pb2.GeneralRequest.FromString,
                    response_serializer=service__pb2.Broadcast.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'lobby.Lobby', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Lobby(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Handle(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/lobby.Lobby/Handle',
            service__pb2.GeneralRequest.SerializeToString,
            service__pb2.GeneralResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Subscribe(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/lobby.Lobby/Subscribe',
            service__pb2.GeneralRequest.SerializeToString,
            service__pb2.Broadcast.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
