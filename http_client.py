#!/usr/bin/env python3.10.8
# -*- coding: utf-8 -*-
'''

Create an HTTP client that will accept the resource URL, method type, and dictionary as passed data (optional). Execute a request with the received method for the received resource, pass data in the appropriate way, and print the status code, headers, and response body to the console.

@author: ~vimer
'''
import requests, re


class URLValueError(ValueError):
    pass


class InputData:
    def __init__(self) -> None:
        self._url: str = None
        self._method: str = None
        self._data: dict = None
    
    def __input_url(self) -> None:
        url = input('input url address: ')
        regex = r'^(http)s?(://)[A-Za-z\-\/\d\.]+$'
        if not bool(re.search(regex, url)):
            msg_error = 'not correct address!'
            raise URLValueError(msg_error)
        self._url = url
    
    def __convert_dict(self, data: str) -> None:
        data = data.strip('{}')
        data = data.split(', ')
        data = [d.split(': ') for d in data]
        self._data = dict(data)
    
    def __input_data(self) -> None:
        print('example input parameters -- "{first_name: Test, last_name: Testerenko}"')
        data = input('input parametrs url: ')
        if data == '': self._data = ' '
        else:
            regex = r'^{(\w+:\s[\w\.\-]+)(\,\s\w+:\s[\w\.\-]+)*}$'
            if data != '' and not bool(re.search(regex, data)):
                msg_error = 'not correct data!'
                raise URLValueError(msg_error)
            self.__convert_dict(data)

    def __input_method(self) -> None:
        method_request = input('input method request: ')
        if not method_request in self._methods:
            msg_error = 'not correct method!'
            raise URLValueError(msg_error)
        self._method = method_request
    
    def _input_client(self) -> None:
        while True:
            try:
                if not self._url: self.__input_url()
                if not self._data: self.__input_data()
                if not self._method: self.__input_method()
                break
            except URLValueError as error:
                print(error)
                continue


class OutputData:
    @staticmethod
    def __output(header, body):
        header = f'*** {header} ***'
        footer = '*' * len(header)
        out_msg = f'''
        
{header}

{body}

{footer}

        '''
        print(out_msg)
    
    def __output_headers(self):
        headers = ''
        for key, value in self._response.headers.items():
            headers += f'{key}: {value}\n\n'
        OutputData.__output('HEADERS', headers[:-4])
    
    def __output_body(self):
        print(self._response.text)
    
    def _output_client(self):
        OutputData.__output('STATUS CODE', self._response.status_code)
        self.__output_headers()
        self.__output_body()


class RequestData(InputData, OutputData):
    def __init__(self):
        super().__init__()
        self._methods = {
            'get': self.__get_request,
            'post': self.__post_request,
            'put': self.__put_request,
            'delete': self.__delete_request,
            'patch': self.__patch_request
        }
        self._response: requests = None
    
    @staticmethod
    def __parameters(func):
        def new_func(self):
            if self._data == ' ': self._data = None
            return func(self)
        return new_func

    @__parameters
    def __get_request(self):
        self._response = requests.get(self._url, self._data)
    
    @__parameters
    def __post_request(self):
        self._response = requests.post(self._url, self._data)
    
    @__parameters
    def __put_request(self):
        self._response = requests.put(self._urls, self._data)
    
    @__parameters
    def __delete_request(self):
        self._response = requests.delete(self._url, self._data)
    
    @__parameters
    def __patch_request(self):
        self._response = requests.patch(self._url, self._data)
    
    def __exit(self) -> bool:
        while True:
            result = input('exit y/n: ')
            if result == 'y': return True
            elif result == 'n': return False

    def _interface(self) -> None:
        while True:
            self._input_client()
            print(self._data)
            self._methods[self._method]()
            self._output_client()
            if self.__exit(): break


if __name__ == '__main__':
    client = RequestData()
    client._interface()
