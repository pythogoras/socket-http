#!/usr/bin/env python3.10.8
# -*- coding: utf-8 -*-
'''

Створити UNIX сервер, котрий приймає повідомлення з двума числами, розділеними
комами. Сервер повинний конвертувати строкове повідомлення в два числа і 
додавати їх. Після вдалого додавання повертати відповідь клієнту.

@author: ~vimer
''' 
import socket, socketserver, os, sys, random, string


class Server(socketserver.BaseRequestHandler):
    def __req_sum(self, data: bytes) -> float:
        list_bytes = data.split(b', ')
        if len(list_bytes) != 3:
            raise Exception('expected 3 arguments')
        list_float = [float(i) for i in list_bytes[:-1]]
        self.client_address = str(list_bytes[-1], 'utf-8')
        return sum(list_float)
    
    def __create_resp(self, data: bytes) -> bytes:
        summa = self.__req_sum(data)
        return f'Добуток чисел: {summa}'.encode(encoding='utf-8')
    
    def handle(self):
        data, sock = self.request
        summa = self.__create_resp(data)
        sock.sendto(summa, self.client_address)


class Client():
    def __init__(self, server_address: str):
        self.__sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.__serve_address = server_address
        self.__client_address: str = None
    
    def __generate_value(self) -> tuple:
        self.__generate_address()
        args = (1.0, 10.0)
        value = [
            str(random.uniform(*args)),
            str(random.uniform(*args)),
            self.__client_address
        ]
        return (', '.join(value), ', '.join(value[:-1]))
    
    def __generate_address(self) -> str:
        data = list(string.ascii_uppercase) + list(string.digits)
        ident = ''.join(random.choices(data, k=10))
        self.__client_address = ident + '.client'
    
    def _close(self):
        self.__sock.close()
        os.remove(self.__client_address)
    
    def _send(self):
        value, numbers = self.__generate_value()
        self.__sock.bind(self.__client_address)
        print(f'Згенеровано два значення: {numbers}')
        self.__sock.sendto(value.encode(encoding='utf-8'), self.__serve_address)
        print(str(self.__sock.recv(1024), 'utf-8'))
        self._close()


if __name__ == '__main__':
    def start(arg):
        '''
        Приклад запуску: python3 udp_unix.py arg
        arg може бути або "client" або "server"
        client -- запускає клієнт сокет
        server -- запускає сервер сокет
        '''
        ARG = ('server', 'client')
        try:
            if len(sys.argv) != 2:
                raise Exception('expected 1 argument')
            elif arg not in ARG:
                raise Exception('unknown argument')
        except Exception as error:
            print(error)
        if arg == ARG[0]:
            try:
                server = socketserver.UnixDatagramServer('sock.server', Server)
                server.serve_forever()
            except KeyboardInterrupt:
                os.remove(server.server_address)
                server.server_close()
                print('exit server')
        elif arg == ARG[1]:
            try:
                client = Client('sock.server')
                client._send()
            except KeyboardInterrupt:
                client._close()
                print('exit client')
                
    start(sys.argv[1])    
