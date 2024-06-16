from concurrent import futures
import grpc
import Client_Server_pb2
import Client_Server_pb2_grpc

from ServerService import server_service

class RedisServiceServicer(Client_Server_pb2_grpc.RedisServiceServicer):
    def RegisterClient(self, request, context):
        success, message = server_service.register_client(request)
        return Client_Server_pb2.RegisterResponse(success=success, message=message)

    def GiveParameters(self, request, context):
        client_params = server_service.give_params(request.name)
        if client_params:
            return Client_Server_pb2.ClientParams(ip=client_params['ip'], port=client_params['port'])
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('No se ha encontrado al cliente')
            return Client_Server_pb2.ClientParams()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Client_Server_pb2_grpc.add_RedisServiceServicer_to_server(RedisServiceServicer(), server)
    server.add_insecure_port('localhost:50051')
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()

serve()