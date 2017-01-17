#!/bin/python
#-*-coding:utf-8-*-
from asyncio import Protocol

class AsProtocal(Protocol):
    def connection_made(self, transport):
        pass

    def connection_lost(self, exc):
        pass

    def data_received(self, data):
        pass

    def eof_received(self):
        pass
