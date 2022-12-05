#!/usr/bin/env python3.10.8
# -*- coding: utf-8 -*-
"""

Create a UDP server that listens for new devices on the network. 
He accepts messages of a specific format, which will be the device ID, and prints
new connections to the console. 
Create a UDP client that will send a unique device ID to the server, notifying 
its presence.

@author: ~vimer
"""
import socket, socketserver, random, string, sys, re


class Client():
    def __init__(self, server_address: tuple):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__address = server_address
    
    def __unical_indenti(self) -> bytes:
        data = list(string.ascii_uppercase) + list(string.digits)
        ident = ''.join(random.choices(data, k=10)).encode(encoding='utf-8')
        return ident
    
    def _close(self):
        self.__sock.close()
    
    def _send(self):
        self.__sock.sendto(self.__unical_indenti(), self.__address)
        self._close()


class ServerUDPHandler(socketserver.BaseRequestHandler): 
    def __valid_request(self):
        regex = b'^[A-Z\d]{10}$'
        if not re.search(regex, self.request[0]):
            raise Exception('not valid request')
    
    def handle(self):
        self.__valid_request()
        data = self.request[0].decode('utf-8')
        print(f'Пристрій {data} приєднався')


def valid_sys_arg(arg, ARG):
    if len(sys.argv) != 2:
        raise Exception('expected 1 argument')
    elif arg not in ARG:
        raise Exception('unknown argument')

def start_server():
    try:
        with socketserver.UDPServer(('127.0.0.1', 8888), ServerUDPHandler) \
        as server:
            server.serve_forever()
    except KeyboardInterrupt:
        print('server exit')

def start_client():
    try:
        address = ('127.0.0.1', 8888)
        client = Client(address)
        client._send()
    except KeyboardInterrupt:
        client._close()
        print('client exit')

if __name__ == '__main__':
    def start(arg):
        '''
        Приклад запуску: python3 udp1.py arg
        arg може бути або "client" або "server"
        client -- запускає клієнт сокет
        server -- запускає сервер сокет
        '''
        ARG = ('server', 'client')
        try:
            valid_sys_arg(arg, ARG)
        except Exception as error:
            print(error)
        if arg == ARG[0]:
            start_server()
        elif arg == ARG[1]:
            start_client()
    
    start(sys.argv[1])
