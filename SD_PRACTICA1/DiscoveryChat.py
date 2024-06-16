import tkinter as tk
from tkinter import Toplevel, Text, Entry, Button, messagebox
import pika
import json

class DiscoveryChat:
    def __init__(self, master, name):
        self.master = master
        self.name = name

        # Crear una nueva ventana vinculada al master
        self.window = Toplevel(self.master)
        self.window.title(f"Discovery Chat")
        self.window.geometry("400x300")

        # Área de texto para mostrar mensajes
        self.chat_history = Text(self.window, state='disabled', width=50, height=10)
        self.chat_history.pack(pady=10)

        # Campo de entrada para escribir mensajes
        self.message_entry = Entry(self.window, width=40)
        self.message_entry.pack(pady=5)

        #Botón para recibir insultos
        send_button = Button(self.window, text="Recibir", command=self.start_consuming)
        send_button.pack()

        # Manejar el cierre de la ventana
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Conectar a RabbitMQ
        self.connect_rabbitmq()

        #Publicar evento
        self.publish_event()

    def connect_rabbitmq(self):
        try:
            # Establecer conexión con RabbitMQ
            self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            self.channel = self.connection.channel()

            # Declarar el exchange y la cola
            self.channel.exchange_declare(exchange='discovery_chat', exchange_type='fanout')
            
            # Cola duradera y no exclusiva para cada usuario
            result = self.channel.queue_declare(queue='', exclusive=True)
            self.queue_name = result.method.queue
            # Vincular la cola del usuario al exchange
            self.channel.queue_bind(exchange='discovery_chat', queue=self.queue_name)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar a RabbitMQ: {str(e)}")
            self.window.destroy()

    def publish_event(self):
        discovery_event = {'sender': self.name, 'message': 'discovery_event', 'queue_name' : self.queue_name}
        self.channel.basic_publish(exchange='discovery_chat',
                                           routing_key='',
                                           body=json.dumps(discovery_event))
    def start_consuming(self):
        print(' [*] Waiting for messages. To exit press CTRL+C')
        def callback(ch, method, properties, body):
            message_data = json.loads(body)
            sender = message_data.get('sender')
            message = message_data.get('message')
            ip = message_data.get('ip')
            port = message_data.get('port')
            private_chats = message_data.get('private_chats', {})
            group_chats_persistent = message_data.get('group_chats_persistent', {})
            group_chats_transient = message_data.get('group_chats_transient', {})
            insult_channel = message_data.get('insult_channel', {})
            if sender != self.name and message == 'discovery_chat_response':
                self.display_message(f"{sender} - IP: {ip}, Puerto: {port}")
                print(f"IP: {ip}, Puerto: {port}")
                if private_chats:
                    for chat in private_chats:
                        self. display_message(f"Chat privado: {chat}")
                if group_chats_persistent:
                    for chat in group_chats_persistent:
                        self.display_message(f"Chat grupal persistente: {chat}")
                if group_chats_transient:
                    for chat in group_chats_transient:
                        self.display_message(f"Chat grupal transitorio: {chat}")
                if insult_channel:
                    for insult_channel in insult_channel:
                        self.display_message(f"Canal de insultos: {insult_channel}")
                    

        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    def display_message(self, message):
        self.chat_history.config(state='normal')
        self.chat_history.insert('end', message + "\n")
        self.chat_history.config(state='disabled')
        self.chat_history.see(tk.END)

    def on_close(self):
        self.window.withdraw()
        self.is_running = False
        try:
            self.channel.close()
            self.connection.close()
        except Exception as e:
            print(f"Error al cerrar la conexión: {str(e)}")

class DiscoveryChatResponse:
    def __init__(self, master, name, ip, port, private_chats, group_chats_persistents, group_chats_transient, insult_channel):
        self.master = master
        self.name = name
        self.ip = ip
        self.port = port
        self.private_chats = private_chats
        self.group_chats_persistents = group_chats_persistents
        self.group_chats_transient = group_chats_transient
        self.insult_channel = insult_channel

        # Conectar a RabbitMQ
        self.connect_rabbitmq()

        #Publicar evento
        self.publish_event()

    def connect_rabbitmq(self):
        try:
            # Establecer conexión con RabbitMQ
            self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            self.channel = self.connection.channel()

            # Declarar el exchange y la cola
            self.channel.exchange_declare(exchange='discovery_chat', exchange_type='fanout')
            
            # Cola duradera y no exclusiva para cada usuario
            result = self.channel.queue_declare(queue='', exclusive=True)
            self.queue_name = result.method.queue
            # Vincular la cola del usuario al exchange
            self.channel.queue_bind(exchange='discovery_chat', queue=self.queue_name)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar a RabbitMQ: {str(e)}")
            self.window.destroy()

    def publish_event(self):
        def response(ch, method, properties, body):
            print(' [*] Waiting for messages. To exit press CTRL+C')
            message_data = json.loads(body)
            sender = message_data.get('sender')
            message = message_data.get('message')
            queue = message_data.get('queue_name')
            if message == 'discovery_event':
                message_response = {'sender': self.name, 'message': 'discovery_chat_response', 'ip' : self.ip, 'port' : self.port, 
                                    'private_chats' : self.private_chats, 'group_chats_persistent' : self.group_chats_persistents,
                                    'group_chats_transient' : self.group_chats_transient, 'insult_channel' : self.insult_channel}
                self.channel.basic_publish(exchange='',
                                           routing_key=queue,
                                           body=json.dumps(message_response))
                print("Enviando respuesta...")

        self.channel.basic_consume(queue=self.queue_name, on_message_callback=response, auto_ack=True)
        self.channel.start_consuming()

        self.connection.close()

    def display_message(self, message):
        self.chat_history.config(state='normal')
        self.chat_history.insert('end', message + "\n")
        self.chat_history.config(state='disabled')
        self.chat_history.see(tk.END)