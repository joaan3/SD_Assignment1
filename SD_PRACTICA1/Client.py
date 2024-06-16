import tkinter as tk
from tkinter import Toplevel, simpledialog, messagebox, Label, Entry, Button
import grpc
import Client_Server_pb2
import Client_Server_pb2_grpc
import ipaddress
from ChatPrivado import ChatPrivado, ChatPrivado2
import ChatPrivado_pb2_grpc
import threading
from concurrent import futures
import ChatPrivadoServicer
from GroupChatTransient import GroupChatTransient
from GroupChatPersistent import GroupChatPersistent
from InsultChannel import InsultChannel
from DiscoveryChat import DiscoveryChat, DiscoveryChatResponse
import sys

class Client(tk.Tk, ChatPrivado_pb2_grpc.ChatServiceServicer):
    def __init__(self, name=None, ip=None, port=None):
        super().__init__()
        #Creamos la ventana inicial del programa
        self.title("Cliente")
        self.geometry("300x300")

        Label(self, text="Nombre:").pack(padx=10, pady=5)
        self.name_entry = Entry(self)
        self.name_entry.pack(padx=10, pady=5)

        Label(self, text="IP:").pack(padx=10, pady=5)
        self.ip_entry = Entry(self)
        self.ip_entry.pack(padx=10, pady=5)

        Label(self, text="Puerto:").pack(padx=10, pady=5)
        self.port_entry = Entry(self)
        self.port_entry.pack(padx=10, pady=5)

        self.connect_button = Button(self, text="Conectar", command=self.connection_to_server)
        self.connect_button.pack(padx=10, pady=10)

        self.stub = None
        #Chats de cada usuario
        self.private_chats = {}
        self.group_chatsTransients = {}
        self.group_chatsPersistents = {}
        self.insult_channels = {}

        if name and ip and port:
            self.name_entry.insert(0, name)
            self.ip_entry.insert(0, ip)
            self.port_entry.insert(0, port)
            self.connection_to_server()

    def connection_to_server(self):
        self.name = self.name_entry.get()
        self.ip = self.ip_entry.get()
        self.port = self.port_entry.get()

        if not self.name or not self.ip or not self.port:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        try:
            self.port = int(self.port)
            ipaddress.ip_address(self.ip)  # Esto lanzará ValueError si la IP no es válida
            if not (1 <= self.port <= 65535):
                raise ValueError("El puerto debe estar entre 1 y 65535.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        connection_str = f'localhost:50051'
        try:
            channel = grpc.insecure_channel(connection_str)
            self.stubServer = Client_Server_pb2_grpc.RedisServiceStub(channel)
            self.registerme()
        except grpc.RpcError as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar: {str(e)}")

    def registerme(self):
        parameters = Client_Server_pb2.ClientInfo(name=self.name, ip=self.ip, port=self.port)
        response = self.stubServer.RegisterClient(parameters)
        if response.success:
            messagebox.showinfo("Registro", "Registro exitoso")
            thread = threading.Thread(target=self.start_grpc_server)
            thread.daemon = True
            thread.start()
            self.hide_main_window()
            self.show_options()
        else:
            messagebox.showerror("Registro", response.message)
                

    def start_grpc_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        ChatPrivado_pb2_grpc.add_ChatServiceServicer_to_server(chat_servicer, server)
        server.add_insecure_port(f'{self.ip}:{self.port}')
        server.start()
        print(f"Server started on port {self.port}")
        server.wait_for_termination()

    def give_params(self, name):
        name_request = Client_Server_pb2.ClientName(name=name)
        response = self.stubServer.GiveParameters(name_request)
        messagebox.showinfo("Datos Recibidos", f"IP: {response.ip}, Puerto: {response.port}")
        return response.ip, response.port

    def show_options(self):
        # Crear una nueva ventana para las opciones
        options_window = Toplevel(self)
        options_window.title("Opciones del Cliente")
        options_window.geometry("300x400")

        Button(options_window, text="Iniciar chat privado", command=self.chat_privado).pack(pady=5)
        Button(options_window, text="Connectar a un chat privado", command=self.chat_privado2).pack(pady=5)
        Button(options_window, text="Chat grupalesTransient", command=self.chat_grupalesTransient).pack(pady=5)
        Button(options_window, text="Chat grupalesPersistent", command=self.chat_grupalesPersistent).pack(pady=5)
        Button(options_window, text="Chat discovery", command=self.chat_discovery).pack(pady=5)
        Button(options_window, text="Chat discovery Response", command=self.chat_discovery_response).pack(pady=5)
        Button(options_window, text="Insult Channel", command=self.insult_channel).pack(pady=5)

    def hide_main_window(self):
        # Oculta la ventana principal
        self.withdraw() 

    def ask_for_name(self):
        # Solicita el nombre del otro usuario para realizar el chat privado
        return simpledialog.askstring("Nombre", "Ingrese el nombre del otro usuario:", parent=self)
    
    def ask_for_groupName(self):
        # Solicita el nombre del grupo
        return simpledialog.askstring("Nombre", "Ingrese el nombre del grupo:", parent=self)

    def chat_privado(self):
        other_name = self.ask_for_name()
        if other_name:
            if other_name == self.name:
                messagebox.showerror("Error", "No puedes chatear contigo mismo")
                return
            else:
                try:
                    self.register_chat(other_name, 1)
                except grpc.RpcError as e:
                    if e.code() == grpc.StatusCode.NOT_FOUND:
                        # Mostrar mensaje personalizado si el error es NOT_FOUND
                        messagebox.showerror("Error", "No se ha encontrado al cliente")
                        print("Error details: Cliente no encontrado")
                    else:
                        # Manejo de otros errores gRPC
                        messagebox.showerror("Error", f"No se pudo obtener la información del otro cliente: {str(e)}")
                        print(f"Error details: {e}")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo obtener la información del otro cliente: {str(e)}")
                    print(f"Error details: {e}")

    def chat_privado2(self):
        other_name = self.ask_for_name()
        if other_name:
            if other_name == self.name:
                messagebox.showerror("Error", "No puedes chatear contigo mismo")
                return
            else:
                try:
                    self.register_chat(other_name, 2)
                except grpc.RpcError as e:
                    if e.code() == grpc.StatusCode.NOT_FOUND:
                        # Mostrar mensaje personalizado si el error es NOT_FOUND
                        messagebox.showerror("Error", "No se ha encontrado al cliente")
                        print("Error details: Cliente no encontrado")
                    else:
                        # Manejo de otros errores gRPC
                        messagebox.showerror("Error", f"No se pudo obtener la información del otro cliente: {str(e)}")
                        print(f"Error details: {e}")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo obtener la información del otro cliente: {str(e)}")
                    print(f"Error details: {e}")
    
    def register_chat(self, other_name, num):
        ip2, port2 = self.give_params(other_name)
        chat_id = f"{self.name}:{other_name}"
        # Si ya existe un chat con el mismo nombre, lo mostramos
        if chat_id in self.private_chats:
            chat = self.private_chats[chat_id]
            #Volvemos a mostrar la ventana y nos volvemos a conectar
            chat.display_window()   
            chat.connectar()
        else:
            if num == 1:
                chat = ChatPrivado(self, self.name, self.ip, self.port, other_name, ip2, port2)
            if num == 2:
                chat = ChatPrivado2(self, self.name, self.ip, self.port, other_name, ip2, port2)
            self.private_chats[chat_id] = chat
            self.hide_main_window()

    def chat_grupalesTransient(self):
        nombre_grupo = self.ask_for_groupName()
        if nombre_grupo in self.group_chatsTransients:
            chat_grupal = self.group_chatsTransients[nombre_grupo]
            chat_grupal.window.deiconify()
            chat_grupal.connect_rabbitmq()
        else:
            chat_grupal = GroupChatTransient(self, self.name, nombre_grupo)
            self.group_chatsTransients[nombre_grupo] = chat_grupal
            self.hide_main_window()
    
    def chat_grupalesPersistent(self):
        nombre_grupo = self.ask_for_groupName()
        if nombre_grupo in self.group_chatsPersistents:
            chat_grupal = self.group_chatsPersistents[nombre_grupo]
            chat_grupal.window.deiconify()
            chat_grupal.connect_rabbitmq()
        else:
            chat_grupal = GroupChatPersistent(self, self.name, nombre_grupo)
            self.group_chatsPersistents[nombre_grupo] = chat_grupal
            self.hide_main_window()
        
    def chat_discovery(self):
        DiscoveryChat(self, self.name)
        self.hide_main_window()
    
    def chat_discovery_response(self):
        nombres_chat_privado = {}
        for chat in self.private_chats:
            nombres_chat_privado[chat] = self.private_chats[chat].other_name
        nombres_chat_grupo = {}
        for chat in self.group_chatsPersistents:
            nombres_chat_grupo[chat] = self.group_chatsPersistents[chat].group_name
        nombres_chat_grupo_transitorio = {}
        for chat in self.group_chatsTransients:
            nombres_chat_grupo_transitorio[chat] = self.group_chatsTransients[chat].group_name
        insult_channels = {}
        for insult_channel in self.insult_channels:
            insult_channels[insult_channel] = self.insult_channels[insult_channel].group_name

        DiscoveryChatResponse(self, self.name, self.ip, self.port, nombres_chat_privado, nombres_chat_grupo, nombres_chat_grupo_transitorio, insult_channels)
        self.hide_main_window()

    def insult_channel(self):
        nombre_grupo = self.ask_for_groupName()
        if nombre_grupo in self.insult_channels:
            insult_channel = self.insult_channels[nombre_grupo]
            insult_channel.window.deiconify()
            insult_channel.connect_rabbitmq()
        else:
            insult_channel = InsultChannel(self, self.name, nombre_grupo)
            self.insult_channels[nombre_grupo] = insult_channel
            self.hide_main_window()
        

chat_servicer = ChatPrivadoServicer.ChatPrivadoServicer()
if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else None
    ip = sys.argv[2] if len(sys.argv) > 2 else None
    port = sys.argv[3] if len(sys.argv) > 3 else None
    app = Client(name, ip, port)
    app.mainloop()