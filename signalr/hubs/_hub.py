import json

from signalr.events import EventHook


class Hub:
    def __init__(self, name, connection):
        self.name = name
        self.server = HubServer(name, connection)
        self.client = HubClient(name, connection)


class HubServer:
    def __init__(self, name, connection):
        self.name = name
        self.__connection = connection

    def invoke(self, method, *data):
        response = self.__connection.send({
            'H': self.name,
            'M': method,
            'A': data,
            'I': self.__connection.increment_send_counter()
        })

        return json.loads(response.content)


class HubClient(object):
    def __init__(self, name, connection):
        self.name = name
        self.__handlers = {}

        def handle(**kwargs):
            inner_data = kwargs['M'][0] if 'M' in kwargs and len(kwargs['M']) > 0 else {}
            hub = inner_data['H'] if 'H' in inner_data else ''
            if hub.lower() == self.name.lower():
                method = inner_data['M']
                if method in self.__handlers:
                    arguments = inner_data['A']
                    self.__handlers[method].fire(*arguments)

        connection.received += handle

    def on(self, method, handler):
        if method not in self.__handlers:
            self.__handlers[method] = EventHook()
        self.__handlers[method] += handler

    def off(self, method, handler):
        if method in self.__handlers:
            self.__handlers[method] -= handler


class DictToObj:
    def __init__(self, d):
        self.__dict__ = d