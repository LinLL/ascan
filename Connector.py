#!/bin/python
#-*-coding:utf-8-*-
import asyncio,functools
from AsProtocol import AsProtocal

class Connection:

    def __init__(self, key):
        self._key = key
        self.status = False
        self.fut = None

    def __repr__(self):
        return 'Connection<{}, status:{}>'.format(self._key, self.status)


class BaseConnector:

    def __init__(self, ports=None, conn_timeout=3, limit=50, loop=None):
        self._conn_timeout = conn_timeout
        self._loop = asyncio.get_event_loop() if loop is None else loop
        self._limit = limit
        self._conns = {}
        self._waits = {}
        self._ports = [80,443, 8080,3389,21,22,445,389,8081,27017] if (ports is None) else ports
        self.result = []


    async def __aiter__(self):
        return self

    async def __anext__(self):
        pass
    async def conncet(self, host, port):
        key = (host, port)
        conn = self._conns.get(key)
        if conn is None:
            conn = Connection(key)

        if len(self._conns.keys()) < self._limit:
            self._conns[key] = conn
            status = await self.direct_con(host, port)
            self._conns.pop(key)
        else:
            fut = self._loop.create_future()
            conn.fut = fut
            self._waits[key] = conn
            await conn.fut
            status = await self.direct_con(host, port)

        conn.status = status
        self.result.append(conn)

    async def clear_waits(self):
        while len(self._conns) > 0:
            await asyncio.sleep(self._conn_timeout)
        while len(self._waits) > 0 :
            num_conns = self._limit - len(self._conns)
            if  num_conns > 0 :
                for i in range(num_conns):
                    key, conn = self._waits.popitem()
                    conn.fut.set_result(None)

            await asyncio.sleep(self._conn_timeout)



    async def direct_con(self, host, port):
        try:
            trans, proto = await asyncio.wait_for(
                self._loop.create_connection(lambda: AsProtocal(), host, port),
                timeout=self._conn_timeout, loop=self._loop)
            trans.close()
            return True
        except asyncio.TimeoutError as e:
            return False
        except Exception as e:
            return False

    def scanhost(self, host):
        for port in self._ports:
            self._loop.create_task(self.conncet(host, port))
        self._loop.run_until_complete(self.clear_waits())

if __name__=="__main__":
    loop = asyncio.get_event_loop()
    b = BaseConnector(conn_timeout=3,limit=500,loop=loop)
    b.scanhost("127.0.0.1")
    print(b.result)





