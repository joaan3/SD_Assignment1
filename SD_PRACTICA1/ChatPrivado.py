import tkinter as tk
from tkinter import Toplevel, Text, Entry, Button, messagebox
import grpc
import ChatPrivado_pb2
import ChatPrivado_pb2_grpc
import threading

class ChatPrivado(tk.Toplevel):
    def __init__(self, master, name, ip, port, other_name, other_ip, other_port):
        self.master = master
        self.name = name
        self.ip = ip
        self.port = port
        self.other_name = other_name
        self.other_ip = other_ip
        self.other_port = other_port
        self.running = False

        self.window1 = Toplevel()
        self.window1.title(f"Chat con {other_name}")
        self.window1.geometry("400x300")
        # Área de texto para mostrar mensajes
        self.chat_history1 = Text(self.window1, state='disabled', width=50, height=10)
        self.chat_history1.pack(pady=10)
        # Campo de entrada para escribir mensajes
        self.message_entry1 = Entry(self.window1, width=40)
        self.message_entry1.pack(pady=5)
        # Botón para enviar mensajes
        send_button = Button(self.window1, text="Enviar", command=self.send_message)
        send_button.pack()

        self.window1.protocol("WM_DELETE_WINDOW", self.on_close)

        self.connectar()

    def connectar(self):
        self.channel = grpc.insecure_channel(f'{self.ip}:{self.port}')
        self.stub = ChatPrivado_pb2_grpc.ChatServiceStub(self.channel)
        self.running = True
        self.receive_thread = self.start_receiving_messages()
    
    def send_message(self):
        message = self.message_entry1.get()
        if message:
            try:
                request = ChatPrivado_pb2.ChatMessage(sender=self.name, receiver=self.other_name, ip=self.other_ip, port=str(self.other_port), message=message)
                response = self.stub.SendMessage(request)
                if response.success:
                    self.display_message(f"Tú: {message}")
                else:
                    print(f"Error al enviar mensaje: {response.response}")  
                    messagebox.showerror("Error al enviar", "No se pudo enviar el mensaje")
                self.message_entry1.delete(0, 'end')
            except grpc.RpcError as e:
                messagebox.showerror("Error de conexión", f"No se pudo enviar el mensaje: {str(e)}")

    def start_receiving_messages(self):
        def receive_messages():
            while self.running:
                try:
                    request = ChatPrivado_pb2.ChatMessage(sender=self.name, receiver=self.other_name)
                    response = self.stub.ReceiveMessage(request)
                    msg = response.response
                    if response.success:
                        self.display_message(f"{self.other_name}: {msg}")
                except grpc.RpcError as e:
                    messagebox.showerror("Error de conexión", f"No se pudo recibir mensajes: {str(e)}")
                    break
        
        self.thread = threading.Thread(target=receive_messages)
        self.thread.daemon = True
        self.thread.start()

    def display_message(self, message):
        self.chat_history1.config(state='normal')
        self.chat_history1.insert('end', message + "\n")
        self.chat_history1.config(state='disabled')
        self.chat_history1.see(tk.END) 

    def display_window(self):
        self.window1.deiconify()

    def on_close(self):
        self.window1.withdraw()
        self.running = False
        if self.receive_thread and threading.Thread.is_alive(self.receive_thread):
            self.receive_thread.join() 
        if self.thread and threading.Thread.is_alive(self.thread):
            self.thread.join()
        self.channel.close()
        self.stub = None

class ChatPrivado2(tk.Toplevel):
    def __init__(self, master, name, ip, port, other_name, other_ip, other_port):
        self.master = master
        self.name = name
        self.ip = ip
        self.port = port
        self.other_name = other_name
        self.other_ip = other_ip
        self.other_port = other_port
        self.running = False

        self.window1 = Toplevel()
        self.window1.title(f"Chat con {other_name}")
        self.window1.geometry("400x300")
        # Área de texto para mostrar mensajes
        self.chat_history1 = Text(self.window1, state='disabled', width=50, height=10)
        self.chat_history1.pack(pady=10)
        # Campo de entrada para escribir mensajes
        self.message_entry1 = Entry(self.window1, width=40)
        self.message_entry1.pack(pady=5)
        # Botón para enviar mensajes
        send_button = Button(self.window1, text="Enviar", command=self.send_message)
        send_button.pack()

        self.window1.protocol("WM_DELETE_WINDOW", self.on_close)

        self.connectar()

    def connectar(self):
        self.channel = grpc.insecure_channel(f'{self.other_ip}:{self.other_port}')
        self.stub = ChatPrivado_pb2_grpc.ChatServiceStub(self.channel)
        self.running = True 
        self.receive_thread = self.start_receiving_messages()
    
    def send_message(self):
        message = self.message_entry1.get()
        if message:
            try:
                request = ChatPrivado_pb2.ChatMessage(sender=self.name, receiver=self.other_name, ip=self.other_ip, port=str(self.other_port), message=message)
                response = self.stub.SendMessage(request)
                if response.success:
                    self.display_message(f"Tú: {message}")
                else:
                    print(f"Error al enviar mensaje: {response.response}")  
                    messagebox.showerror("Error al enviar", "No se pudo enviar el mensaje")
                self.message_entry1.delete(0, 'end')
            except grpc.RpcError as e:
                messagebox.showerror("Error de conexión", f"No se pudo enviar el mensaje: {str(e)}")

    def start_receiving_messages(self):
        def receive_messages():
            while self.running:
                try:
                    request = ChatPrivado_pb2.ChatMessage(sender=self.name, receiver=self.other_name)
                    response = self.stub.ReceiveMessage(request)
                    msg = response.response
                    if response.success:
                        self.display_message(f"{self.other_name}: {msg}")
                except grpc.RpcError as e:
                    messagebox.showerror("Error de conexión", f"No se pudo recibir mensajes: {str(e)}")
                    break

        self.thread = threading.Thread(target=receive_messages)
        self.thread.daemon = True
        self.thread.start()

    def display_message(self, message):
        self.chat_history1.config(state='normal')
        self.chat_history1.insert('end', message + "\n")
        self.chat_history1.config(state='disabled')
        self.chat_history1.see(tk.END) 

    def display_window(self):
        self.window1.deiconify()

    def on_close(self):
        self.window1.withdraw()
        self.running = False
        if self.receive_thread and threading.Thread.is_alive(self.receive_thread):
            self.receive_thread.join() 
        if self.thread and threading.Thread.is_alive(self.thread):
            self.thread.join()
        self.channel.close()
        self.stub = None