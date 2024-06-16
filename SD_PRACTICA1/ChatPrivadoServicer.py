import ChatPrivado_pb2_grpc
import ChatPrivado_pb2

class ChatPrivadoServicer(ChatPrivado_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        self.messages = {}  # Diccionario para almacenar mensajes por chat

    def SendMessage(self, request, context):
        chat_id = f"{request.sender}:{request.receiver}"
        if chat_id not in self.messages:
            self.messages[chat_id] = []
        self.messages[chat_id].append(request.message)
        return ChatPrivado_pb2.ChatResponse(success=True)

    def ReceiveMessage(self, request, context):
        chat_id = f"{request.receiver}:{request.sender}"
        if chat_id in self.messages and self.messages[chat_id]:
            message = self.messages[chat_id].pop(0)
            return ChatPrivado_pb2.ChatResponse(success=True, response=message)
        else:
            return ChatPrivado_pb2.ChatResponse(success=False, response="No new messages")