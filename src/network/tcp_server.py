import asyncio
import logging
import socket
import functools

from asyncio_extras import async_contextmanager, yield_async

logger = logging.getLogger(__name__)

_Servers = {}

class TcpServer(asyncio.Protocol):
    
    HOST = "127.0.0.1"
    PORT = 8888
    
    def __init__(self):
        self.transport = None
            
    def connection_lost(self, exec):
        """
        Callback when the connection is lost
        
        Args:
            exc: <Exception> or None
        """
        peername = self.transport.get_extra_info('peername')
        logger.info('Connection lost from {}: {}'.format(peername, exec))
        self.transport = None
    
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        logger.info('Connection made from {}'.format(peername))
        self.transport = transport
    
    @classmethod
    async def create_server(cls, host=None, port=None):
        if not host:
            host = cls.HOST
        if not port:
            port = cls.PORT
        loop = asyncio.get_event_loop()
        return await loop.create_server(functools.partial(cls.factory, host, port), host, port)
        
    def data_received(self, data):
        message = data.decode()
        logger.info('Data Received: {!r}'.format(data.hex()))
        
    @classmethod
    def factory(cls, host, port):
        if not _Servers.get((host, port)):
            _Servers[(host, port)] = cls()
        return _Servers[(host, port)]
        
    def send_data(self, data):
        self.transport.write(data)

    @classmethod    
    @async_contextmanager
    async def serve(cls, protocol, host=None, port=None):
        server = await cls.create_server(host, port)
        await yield_async(cls.factory(host, port)) # can directly use yield since 3.6
        server.close()
