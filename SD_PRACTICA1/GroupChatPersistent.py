import tkinter as tk
from tkinter import Toplevel, Text, Entry, Button, messagebox
import pika
import json

class GroupChatPersistent:
    def __init__(self, master, name, group_name):
        self.master = master
        self.name = name
        self.group_name = group_name
        self.user_queue_name = f"{name}_{group_name}_queue_persistent"  # Cola específica y duradera para el usuario

        # Crear una nueva ventana vinculada al master
        self.window = Toplevel(self.master)
        self.window.title(f"Chat grupal: {group_name}")
        self.window.geometry("400x300")

        # Área de texto para mostrar mensajes
        self.chat_history = Text(self.window, state='disabled', width=50, height=10)
        self.chat_history.pack(pady=10)

        # Campo de entrada para escribir mensajes
        self.message_entry = Entry(self.window, width=40)
        self.message_entry.pack(pady=5)

        # Botón para enviar mensajes
        send_button = Button(self.window, text="Enviar", command=self.send_message)
        send_button.pack()

        # Manejar el cierre de la ventana
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Conectar a RabbitMQ
        self.connect_rabbitmq()

    def connect_rabbitmq(self):
        try:
            self.is_running = True
            # Establecer conexión con RabbitMQ
            self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            self.channel = self.connection.channel()

            # Declarar el exchange y la cola
            self.channel.exchange_declare(exchange=self.group_name, exchange_type='fanout', durable=True)
            
            # Cola duradera y no exclusiva para cada usuario
            self.channel.queue_declare(queue=self.user_queue_name, durable=True, exclusive=False)

            # Vincular la cola del usuario al exchange
            self.channel.queue_bind(exchange=self.group_name, queue=self.user_queue_name)

            # Cargar mensajes existentes
            self.load_existing_messages()

            # Comenzar a consumir mensajes
            self.check_new_messages()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar a RabbitMQ: {str(e)}")
            self.window.destroy()

    def load_existing_messages(self):
        try:
            # Obtener todos los mensajes de la cola del usuario
            method_frame, header_frame, body = self.channel.basic_get(queue=self.user_queue_name, auto_ack=False)
            while method_frame:
                message_data = json.loads(body)
                sender = message_data['sender']
                message = message_data['message']
                self.display_message(f"{sender}: {message}")
                method_frame, header_frame, body = self.channel.basic_get(queue=self.user_queue_name, auto_ack=False)
        except Exception as e:
            print(f"Error al cargar mensajes existentes: {str(e)}")

    def send_message(self):
        message = self.message_entry.get()
        if message:
            try:
                message_data = {'sender': self.name, 'message': message}
                self.channel.basic_publish(exchange=self.group_name,
                                           routing_key='',
                                           body=json.dumps(message_data),
                                           properties=pika.BasicProperties(delivery_mode=2))  # Mensaje persistente
                self.message_entry.delete(0, 'end')
            except Exception as e:
                messagebox.showerror("Error de conexión", f"No se pudo enviar el mensaje: {str(e)}")

    def check_new_messages(self):
        if self.is_running:
            try:
                method, properties, body = self.channel.basic_get(queue=self.user_queue_name, auto_ack=True)
                if body is not None:
                    message_data = json.loads(body)
                    sender = message_data['sender']
                    message = message_data['message']
                    if sender == self.name:
                        sender = 'Tú'
                    self.display_message(f"{sender}: {message}")
            except pika.exceptions.ChannelClosed:
            # No hacer nada si no hay mensajes nuevos
                pass
            except Exception as e:
                print(f"Error al recibir mensajes: {str(e)}")
            # Programar la siguiente verificación de mensajes después de 100 ms
            self.window.after(100, self.check_new_messages)

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
