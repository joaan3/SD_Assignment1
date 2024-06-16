import redis

class ServerService:
    def __init__(self):
        # Configurar la conexión a Redis
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.redis_client.flushdb() 
        self.redis_client.exists
        self.ids = []

    def register_client(self, client):
        # Asegurarse de que la entrada es válida
        if client.name and client.ip and client.port:
            client_id = f"{client.ip}:{client.port}"
            # No puede haber dos clientes con la misma ip y puerto
            if self.ids.count(client_id) >= 1:
                return False, "Ya existe un cliente con el mismo puerto e id"
            # Guardar en Redis
            self.redis_client.set(client.name, client_id)
            self.ids.append(client_id)
            print(f'Client received = {client.name} at {client_id}')
            return True, "Registro completado"
        else:
            return False, "Las credenciales introducidas no son válidas"

    def give_params(self, name):
        # Verificar si el nombre existe en Redis
        client_id = self.redis_client.get(name)
        if client_id:
            ip, port = client_id.split(':')
            return {'ip': ip, 'port': int(port)}
        else:
            # Si no se encuentra, devolver None o manejar el error
            return None

        
server_service = ServerService()
