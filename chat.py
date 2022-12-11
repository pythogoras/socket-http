#!/usr/bin/env python3.10.8
# -*- coding: utf-8 -*-
'''

Create a simple chat based on the TCP protocol that will allow multiple clients to connect and exchange messages.

@author: ~vimer
'''
import socketserver, re, socket, sys, signal
from datetime import datetime

# *** SERVER ***


class ChatServer(socketserver.BaseRequestHandler):
    clients: dict = {}

    def __init__(self, *arqs, **kwarqs):
        self.__user_name: str = None
        super().__init__(*arqs, **kwarqs)
    
    @staticmethod
    def __form_message(func):

        def new_func(self, data: str, user_name):
            name = 'bot'
            if user_name: name = user_name
            date = datetime.now().isoformat(' ', 'minutes')
            msg = f'''
            
            <{name}>
            ```
                {data}
            
            ```
            {date}

            '''
            return func(self, msg, user_name)

        return new_func

    def __convert_string(self, data: bytes) -> str:
        return str(data, 'utf-8')
    
    def __convert_bytes(self, data: str) -> bytes:
        return data.encode('utf-8')
    
    @__form_message
    def __send(self, data: str, user_name: str or None) -> None:
        data = self.__convert_bytes(data)
        self.request.sendall(data)
    
    def __send_all(self, data: str, user_name: str or None) -> None:
        for _, client in self.clients.items():
            if client != self:
                client.__send(data, user_name)
    
    @staticmethod
    def __valid_name(name: str) -> bool:
        return bool(re.search(r'^\w{3,25}?$', name))
    
    def __response(self) -> str:
        data = self.request.recv(1024)
        data_str = self.__convert_string(data)
        return data_str
    
    def __new_user(self, name: str) -> None:
        if name in ChatServer.clients:
            return self.__send(f'Name {name} taken, please choose another', None)
        elif ChatServer.__valid_name(name):
            ChatServer.clients[name] = self
            self.__send(f'Welcome, {name}', None)
            self.__send_all(f'add user {name}', None)
            self.__user_name = name
        else:
            self.__send(f'{name} - unacceptable symbols. Only alphabetic and numeric characters and the underscore are allowed.', None)
    
    def handle(self) -> None:
        while True:
            if self.__user_name:
                data = self.__response()
                if not data: break
                self.__send_all(data, self.__user_name)
            else:
                self.__send("What's your name?", None)
                name = name = self.__response()
                if not name: break
                self.__new_user(name)

    def finish(self) -> None:
        if self.__user_name:
            self.__send_all(f'user {self.__user_name} exit', None)
            del ChatServer.clients[self.__user_name]


# *** CLIENT ***


class ChatClient():
    def __init__(self, server_address: tuple):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.connect(server_address)
    
    @staticmethod
    def __convert_bytes(data: str) -> bytes:
        return data.encode('utf-8')

    def __send_message(self, msg: str) -> None:
        msg = self.__convert_bytes(msg)
        self.__sock.sendall(msg)
    
    def __input__message(self) -> bool:
        stop: bool = False
        date = datetime.now().isoformat(' ', 'minutes')
        print('<I>')
        print(date)
        msg = input('...')
        if msg == 'exit()':
            self.__close()
            stop = True
        elif msg != '':
            self.__send_message(msg)
        return stop
    
    def __close(self) -> None:
        self.__sock.close()
        print('client exit')
    
    def __print_message(self) -> None or bool:
        try:
            msg = self.__sock.recv(1024)
            print(str(msg, 'utf-8'))
        except KeyboardInterrupt:
            return self.__input__message()
    
    def chat(self) -> None:
        print('for input message CTRL + C')
        print('for exit input "exit()"')
        while True:
            if self.__print_message(): break


def _valid_sys_arg(arg, ARG):
    if len(sys.argv) != 2:
        raise Exception('expected 1 argument')
    elif arg not in ARG:
        raise Exception('unknown argument')

def _start_server():
    with socketserver.ThreadingTCPServer(('127.0.0.1', 8888), ChatServer) as server:
        server.serve_forever()

def _start_client():
    server = ('127.0.0.1', 8888)
    client = ChatClient(server)
    client.chat()
        

if __name__ == '__main__':
    def start(arg):
        ARG = ('server', 'client')
        try:
            _valid_sys_arg(arg, ARG)
        except Exception as error:
            print(error)
        if arg == ARG[0]:
            _start_server()
        elif arg == ARG[1]:
            _start_client()
    
    start(sys.argv[1])
