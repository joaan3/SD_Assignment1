# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import ChatPrivado_pb2 as ChatPrivado__pb2


class ChatServiceStub(object):
  """Servicio que define cómo se enviarán y recibirán los mensajes
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.SendMessage = channel.unary_unary(
        '/ChatPrivado.ChatService/SendMessage',
        request_serializer=ChatPrivado__pb2.ChatMessage.SerializeToString,
        response_deserializer=ChatPrivado__pb2.ChatResponse.FromString,
        )
    self.ReceiveMessage = channel.unary_unary(
        '/ChatPrivado.ChatService/ReceiveMessage',
        request_serializer=ChatPrivado__pb2.ChatMessage.SerializeToString,
        response_deserializer=ChatPrivado__pb2.ChatResponse.FromString,
        )


class ChatServiceServicer(object):
  """Servicio que define cómo se enviarán y recibirán los mensajes
  """

  def SendMessage(self, request, context):
    """RPC para enviar mensajes a otro cliente
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ReceiveMessage(self, request, context):
    """RPC para recibir mensajes del servidor
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_ChatServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'SendMessage': grpc.unary_unary_rpc_method_handler(
          servicer.SendMessage,
          request_deserializer=ChatPrivado__pb2.ChatMessage.FromString,
          response_serializer=ChatPrivado__pb2.ChatResponse.SerializeToString,
      ),
      'ReceiveMessage': grpc.unary_unary_rpc_method_handler(
          servicer.ReceiveMessage,
          request_deserializer=ChatPrivado__pb2.ChatMessage.FromString,
          response_serializer=ChatPrivado__pb2.ChatResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'ChatPrivado.ChatService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
