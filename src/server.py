"""
PyGhost TCP Server
Handles client connections, login, and room management.
"""
import asyncio
import struct
from typing import Dict, Optional
from protocol import (
    OpCode, encode_message, decode_header, decode_packet,
    decode_login_req, encode_login_resp, encode_room_list
)


class ClientSession:
    """Represents a connected client."""
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.pseudo: Optional[str] = None
        self.addr = writer.get_extra_info('peername')
    
    async def send(self, opcode: int, payload: bytes = b''):
        """Send a message to this client."""
        msg = encode_message(opcode, payload)
        self.writer.write(msg)
        await self.writer.drain()


class GhostServer:
    """Async TCP server for PyGhost."""
    
    def __init__(self, host: str = '127.0.0.1', port: int = 5555):
        self.host = host
        self.port = port
        self.clients: Dict[str, ClientSession] = {}  # pseudo -> session
        self.server: Optional[asyncio.Server] = None
    
    async def start(self):
        """Start the server."""
        self.server = await asyncio.start_server(
            self._handle_client, self.host, self.port
        )
        print(f"Server listening on {self.host}:{self.port}")
        async with self.server:
            await self.server.serve_forever()
    
    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle a new client connection."""
        session = ClientSession(reader, writer)
        print(f"Client connected: {session.addr}")
        
        try:
            while True:
                # Read header (4 bytes)
                header = await reader.readexactly(4)
                msg_size = decode_header(header)
                
                # Read body
                body = await reader.readexactly(msg_size)
                opcode, payload = decode_packet(body)
                
                await self._handle_message(session, opcode, payload)
                
        except asyncio.IncompleteReadError:
            print(f"Client disconnected: {session.addr}")
        except Exception as e:
            print(f"Error with client {session.addr}: {e}")
        finally:
            # Cleanup
            if session.pseudo and session.pseudo in self.clients:
                del self.clients[session.pseudo]
            writer.close()
            await writer.wait_closed()
    
    async def _handle_message(self, session: ClientSession, opcode: int, payload: bytes):
        """Process a received message."""
        if opcode == OpCode.REQ_LOGIN:
            await self._handle_login(session, payload)
        elif opcode == OpCode.PONG:
            pass  # Heartbeat response, ignore
        else:
            print(f"Unknown opcode from {session.addr}: {opcode}")
    
    async def _handle_login(self, session: ClientSession, payload: bytes):
        """Handle login request."""
        pseudo = decode_login_req(payload)
        print(f"Login request from {session.addr}: '{pseudo}'")
        
        # Validate pseudo
        if not pseudo or len(pseudo) > 20 or pseudo in self.clients:
            # Refused
            await session.send(OpCode.RESP_LOGIN, encode_login_resp(0x01))
            print(f"Login refused for '{pseudo}'")
            return
        
        # Accept login
        session.pseudo = pseudo
        self.clients[pseudo] = session
        
        await session.send(OpCode.RESP_LOGIN, encode_login_resp(0x00))
        print(f"Login accepted for '{pseudo}'")
        
        # Send empty room list
        await session.send(OpCode.ROOM_LIST, encode_room_list([]))


async def main():
    server = GhostServer()
    await server.start()


if __name__ == '__main__':
    asyncio.run(main())
