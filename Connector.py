#!/bin/python
#-*-coding:utf-8-*-
import asyncio,functools

class Connection:

    def __init__(self, key, transport, timeout, protocol):
        self._transport = transport
        self._timeout = timeout
        self._protocol = protocol
        self._key = key

    def __repr__(self):
        return 'Connection<{}>'.format(self._key)


class BaseConnector:

    def __init__(self, conn_timeout=None, limit=50, loop=None):
        self._conn_timeout = conn_timeout
        self._loop = asyncio.get_event_loop() if loop is None else loop
        self._limit = limit
        self._factory = functools.partial(asyncio.Protocol)

    async def conncet(self, req):
        key = (req.host, req.port)
        self._loop.create_connection()
