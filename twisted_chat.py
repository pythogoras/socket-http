#!/usr/bin/env python3.10.8
# -*- coding: utf-8 -*-
'''

Create a simple chat based on the TCP protocol that will allow multiple clients to connect and exchange messages.

@author: ~vimer
'''
from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory, Factory
from twisted.protocols.basic import LineReceiver
from datetime import datetime
import signal, sys, re

# *** CLIENT ***


class ClientChat(Protocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__name: str = None
    
    def connectionMade(self):
        signal.signal(signal.SIGINT, self.__send_message)
        print('for input message CTRL + C\n')
        print('for exit input "exit"')

    def dataReceived(self, data: bytes):
        print(str(data, 'utf-8'))
    
    def __send_message(self, signum, frame):
        date = datetime.now().isoformat(' ', 'minutes')
        print('<I>')
        print(date)
        msg = input('...')
        if msg == 'exit()':
            self.transport.loseConnection()
            reactor.stop()
        elif msg != '':
            msg += '\r\n'
            self.transport.write(msg.encode(encoding='utf-8'))


class ClientChatFactory(ClientFactory):
    def startedConnecting(self, connector):
        print('...started to connect\n')
    
    def buildProtocol(self, addr):
        print('...connected\n')
        return ClientChat()
    
    def clientConnectionLost(self, connector, reason):
        print(f'...Lost connection.  Reason: {reason}\n')
    
    def clientConnectionFailed(self, connector, reason):
        print('...Connection failed. Reason: {reason}\n')
    
    def doStop(self):
        print('...client exit')


# *** SERVER ***


class ChatServer(LineReceiver):
    def __init__(self, users: dict) -> None:
        self.__users: dict = users
        self.__state: str = 'GETNAME'
        self.__name: str = None
        self.__welcome: str = "What's your name?"
    
    @staticmethod
    def __form_message(func):
        def new_func(self, msg: str, user_name: str or None):
            name: str = 'bot'
            if user_name:
                name = user_name
            date = datetime.now().isoformat(' ', 'minutes')
            msg = f'''

            <{name}>
            ```
                {msg}
                
            ```
            {date}

            '''.encode('utf-8')
            return func(self, msg, name)
        return new_func
    
    @__form_message
    def sendLine(self, line: str, name: str or None):
        return super().sendLine(line)
    
    def connectionMade(self):
        print('...send welcome')
        self.sendLine(self.__welcome, None)
    
    def connectionLost(self, reason):
        if self.__name in self.__users:
            msg = f'user {self.__name} exit'
            del self.__users[self.__name]
            self.__name = None
            self.__send_message(msg)
    
    def __send_message(self, msg):
        for _, protocol in self.__users.items():
            if protocol != self:
                protocol.sendLine(msg, self.__name)
    
    def __valid_name(self, name: str):
        return bool(re.search(r'^\w{3,25}?$', name))
    
    def __handle_getname(self, name: str):
        if name in self.__users:
            self.sendLine(f'Name {name} taken, please choose another', None)
        elif not self.__valid_name(name):
            self.sendLine(f'{name} - unacceptable symbols. Only alphabetic and numeric characters and the underscore are allowed.', None)
        else:
            msg = f'Welcome, {name}'
            self.sendLine(msg, None)
            msg = f'add user {name}'
            self.__send_message(msg)
            self.__name = name
            self.__users[name] = self
            self.__state = 'CHAT'
    
    def lineReceived(self, line):
        print(line)
        line = str(line, 'utf-8')
        print(line)
        if self.__state == 'GETNAME':
            self.__handle_getname(line)
            print('handle_getname')
        elif self.__state == 'CHAT':
            self.__send_message(line)


class ChatFactory(Factory):
    def __init__(self):
        self.__users = {}
    
    def buildProtocol(self, addr):
        return ChatServer(self.__users)


def _valid_sys_arg(arg: str, ARG: list) -> None:
    if len(sys.argv) != 2:
        raise Exception('expected 1 argument')
    elif arg not in ARG:
        raise Exception('unknown argument')

def _start_client():
    reactor.connectTCP('127.0.0.1', 8888, ClientChatFactory())
    reactor.run()

def _start_server():
    reactor.listenTCP(8888, ChatFactory())
    reactor.run()

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
