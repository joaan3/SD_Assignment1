import tkinter as tk
from tkinter import Toplevel, Text, Entry, Button, messagebox
import pika

class InsultChannel:
    def __init__(self, master, name, group_name):
        self.master = master
        self.name = name
        self.group_name = group_name

        # Crear una nueva ventana vinculada al master
        self.window = Toplevel(self.master)
        self.window.title(f"Insult Channel: {group_name}")
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

        #Botón para recibir insultos
        send_button = Button(self.window, text="Recibir", command=self.check_new_messages)
        send_button.pack()

        # Manejar el cierre de la ventana
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # Conectar a RabbitMQ
        self.connect_rabbitmq()

    def connect_rabbitmq(self):
        try:
            # Establecer conexión con RabbitMQ
            self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            self.channel = self.connection.channel()

            # Cola duradera y no exclusiva para cada usuario
            self.channel.queue_declare(queue='task_queue', durable=True)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar a RabbitMQ: {str(e)}")
            self.window.destroy()
    
    def send_message(self):
        message = self.message_entry.get()
        if message:
            try:
                self.channel.basic_publish(exchange='',
                                           routing_key='task_queue',
                                           body=message,
                                           properties=pika.BasicProperties(delivery_mode=2))
                self.message_entry.delete(0, 'end')
            except Exception as e:
                messagebox.showerror("Error de conexión", f"No se pudo enviar el mensaje: {str(e)}")
    
    def check_new_messages(self):
        print(' [*] Waiting for messages. To exit press CTRL+C')
        def callback(ch, method, properties, body):
            msg = body.decode()
            print(f" [x] Received {msg}")
            self.display_message(f"{msg}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue='task_queue', on_message_callback=callback)
        self.channel.start_consuming()
    
    def display_message(self, message):
        self.chat_history.config(state='normal')
        self.chat_history.insert('end', message + "\n")
        self.chat_history.config(state='disabled')
        self.chat_history.see(tk.END)
    
    def on_close(self):
        self.window.withdraw()
        try:
            self.connection.close()
        except Exception as e:
            print(f"Error al cerrar la conexión: {str(e)}")

    