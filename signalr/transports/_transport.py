from abc import abstractmethod
import json
import sys

if sys.version_info[0] < 3:
    from urllib import quote_plus
else:
    from urllib.parse import quote_plus

import gevent


class Transport:
    def __init__(self, session, connection):
        self._session = session
        self._connection = connection

    @abstractmethod
    def _get_name(self):
        pass

    def negotiate(self):
        url = self.__get_base_url(self._connection.url,
                                  self._connection,
                                  'negotiate',
                                  connectionData=self._connection.data)
        negotiate = self._session.get(url)

        return negotiate.json()

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def send(self, data):
        pass

    @abstractmethod
    def close(self):
        pass

    def accept(self, negotiate_data):
        return True

    def _handle_notification(self, message):
        if len(message) == 0:
            return

        data = json.loads(message)
        self._connection.received.fire(**data)
        gevent.sleep(0)

    def _get_url(self, action, **kwargs):
        args = kwargs.copy()
        args['transport'] = self._get_name()
        args['connectionToken'] = self._connection.token
        args['connectionData'] = self._connection.data

        url = self._get_transport_specific_url(self._connection.url)

        return self.__get_base_url(url, self._connection, action, **args)

    def _get_transport_specific_url(self, url):
        return url

    @staticmethod
    def __get_base_url(url, connection, action, **kwargs):
        args = kwargs.copy()
        args['clientProtocol'] = connection.protocol_version
        query = '&'.join(['{key}={value}'.format(key=key, value=quote_plus(args[key])) for key in args])

        return '{url}/{action}?{query}'.format(url=url,
                                               action=action,
                                               query=query)