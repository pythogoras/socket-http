#!/usr/bin/env python3.10.8
# -*- coding: utf-8 -*-
"""

Create a UDP server that listens for new devices on the network. 
He accepts messages of a specific format, which will be the device ID, and prints new connections to the console. 
Create a UDP client that will send a unique device ID to the server, notifying its presence.

@author: ~vimer
"""
import socket, socketserver, random, string, sys


class Client():
    def __init__(self):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__address = ('127.0.0.1', 8888)
        self.__send()
    
    def __unical_indenti(self) -> bytes:
        data = list(string.ascii_uppercase) + list(string.digits)
        ident = ''.join(random.choices(data, k=10)).encode(encoding='utf-8')
        return ident
    
    def __send(self):
        self.__sock.sendto(self.__unical_indenti(), self.__address)


class ServerUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].decode('utf-8')
        print(f'Пристрій {data} приєднався')


if __name__ == '__main__':
    def start(arg):
        '''
        Приклад запуску: python3 udp1.py arg
        arg може бути або "client" або "server"
        client -- запускає клієнт сокет
        server -- запускає сервер сокет
        '''
        ARG = ('server', 'client')
        if len(sys.argv) != 2:
            raise Exception('expected 1 argument')
        elif arg not in ARG:
            raise Exception('unknown argument')
        if arg == ARG[0]:
            with socketserver.UDPServer(('127.0.0.1', 8888), ServerUDPHandler) \
            as server:
                server.serve_forever()
        elif arg == ARG[1]:
            Client()
    
    try:
        start(sys.argv[1])
    except Exception as error:
        print(error)
    except KeyboardInterrupt:
        print('exit server')
