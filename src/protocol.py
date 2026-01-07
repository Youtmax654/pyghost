import struct
from enum import IntEnum
from typing import Optional, Tuple, Any, List
from dataclasses import dataclass

class OpCode(IntEnum):
    REQ_LOGIN = 0x01
    RESP_LOGIN = 0x02
    REQ_JOIN = 0x03
    RESP_ROOM = 0x04
    ROOM_LIST = 0x05
    REQ_LEAVE = 0x06
    NOTIFY = 0x07
    DATA = 0x08
    PING = 0xFD
    PONG = 0xFE
    ERROR = 0xFF

class ProtocolError(Exception):
    pass

@dataclass
class RoomInfo:
    room_id: int
    name: str
    players: int
    max_players: int

def encode_message(opcode: int, payload: bytes) -> bytes:
    """
    Encodes a message into bytes ready to be sent over TCP.
    Format: [Size (4 bytes BE)] [OpCode (1 byte)] [Payload]
    Size includes OpCode + Payload length.
    """
    # Size = 1 byte (OpCode) + len(payload)
    msg_size = 1 + len(payload)
    
    # Header: Size (4 bytes, Big-Endian)
    header = struct.pack('>I', msg_size)
    
    # Body: OpCode (1 byte) + Payload
    body = struct.pack('B', opcode) + payload
    
    return header + body

def decode_header(header_bytes: bytes) -> int:
    """
    Decodes the header to get the message size.
    Expected length of header_bytes: 4
    """
    if len(header_bytes) != 4:
        raise ProtocolError("Invalid header length")
    # Unpack 4 bytes Big-Endian unsigned int
    size = struct.unpack('>I', header_bytes)[0]
    return size

def decode_packet(packet_bytes: bytes) -> Tuple[int, bytes]:
    """
    Decodes a full packet excluding the size header.
    packet_bytes should be the body of the message (OpCode + Payload).
    Returns (opcode, payload).
    """
    if len(packet_bytes) < 1:
        raise ProtocolError("Packet too short (no opcode)")
    
    opcode = packet_bytes[0]
    payload = packet_bytes[1:]
    return opcode, payload

# Specific Message Encoders/Decoders

# 1. Login
def encode_login_req(pseudo: str) -> bytes:
    """C -> S : REQ_LOGIN"""
    return pseudo.encode('utf-8')

def decode_login_req(payload: bytes) -> str:
    return payload.decode('utf-8')

def encode_login_resp(status: int) -> bytes:
    """S -> C : RESP_LOGIN"""
    return struct.pack('B', status)

def decode_login_resp(payload: bytes) -> int:
    if len(payload) < 1:
        raise ProtocolError("Login resp too short")
    return struct.unpack('B', payload)[0]

# 2. Rooms
def encode_room_list(rooms: List[RoomInfo]) -> bytes:
    """
    S -> C : ROOM_LIST
    Payload: [NbRooms (1o)] + N * [ID(4o) + LenName(1o) + Name + Players(1o) + Max(1o)]
    """
    payload = struct.pack('B', len(rooms))
    for room in rooms:
        name_bytes = room.name.encode('utf-8')
        payload += struct.pack('>I', room.room_id)
        payload += struct.pack('B', len(name_bytes))
        payload += name_bytes
        payload += struct.pack('BB', room.players, room.max_players)
    return payload

def decode_room_list(payload: bytes) -> List[RoomInfo]:
    rooms = []
    if len(payload) < 1:
        return rooms
    
    nb_rooms = payload[0]
    offset = 1
    
    for _ in range(nb_rooms):
        # ID (4)
        if offset + 4 > len(payload): raise ProtocolError("RoomList truncated (ID)")
        room_id = struct.unpack('>I', payload[offset:offset+4])[0]
        offset += 4
        
        # LenName (1)
        if offset + 1 > len(payload): raise ProtocolError("RoomList truncated (LenName)")
        len_name = payload[offset]
        offset += 1
        
        # Name
        if offset + len_name > len(payload): raise ProtocolError("RoomList truncated (Name)")
        name = payload[offset:offset+len_name].decode('utf-8')
        offset += len_name
        
        # Players (1), Max (1)
        if offset + 2 > len(payload): raise ProtocolError("RoomList truncated (Stats)")
        players, max_players = struct.unpack('BB', payload[offset:offset+2])
        offset += 2
        
        rooms.append(RoomInfo(room_id, name, players, max_players))
        
    return rooms

def encode_join_req(room_id: int) -> bytes:
    """C -> S : REQ_JOIN"""
    return struct.pack('>I', room_id)

def decode_join_req(payload: bytes) -> int:
    if len(payload) != 4:
         raise ProtocolError("Invalid Join Req payload size")
    return struct.unpack('>I', payload)[0]

def encode_room_resp(players: List[str]) -> bytes:
    """
    S -> C : RESP_ROOM
    Payload: [NbPlayers (1o)] + N * [LenPseudo(1o) + Pseudo]
    """
    payload = struct.pack('B', len(players))
    for p in players:
        p_bytes = p.encode('utf-8')
        payload += struct.pack('B', len(p_bytes)) + p_bytes
    return payload

def decode_room_resp(payload: bytes) -> List[str]:
    if len(payload) < 1:
        return []
    
    nb_players = payload[0]
    offset = 1
    players = []
    
    for _ in range(nb_players):
        if offset + 1 > len(payload): raise ProtocolError("RoomResp truncated (Len)")
        len_p = payload[offset]
        offset += 1
        
        if offset + len_p > len(payload): raise ProtocolError("RoomResp truncated (Pseudo)")
        p = payload[offset:offset+len_p].decode('utf-8')
        offset += len_p
        
        players.append(p)
        
    return players

def encode_leave_req() -> bytes:
    """C -> S : REQ_LEAVE"""
    return b''

def encode_notify(notify_type: int, pseudo: str) -> bytes:
    """
    S -> C : NOTIFY
    Payload: [Type (1o)] + [LenPseudo (1o)] + [Pseudo]
    """
    pseudo_bytes = pseudo.encode('utf-8')
    return struct.pack('B', notify_type) + struct.pack('B', len(pseudo_bytes)) + pseudo_bytes

def decode_notify(payload: bytes) -> Tuple[int, str]:
    if len(payload) < 2:
        raise ProtocolError("Notify payload too short")
    notify_type = payload[0]
    len_pseudo = payload[1]
    if len(payload) < 2 + len_pseudo:
        raise ProtocolError("Notify payload truncated")
    pseudo = payload[2:2+len_pseudo].decode('utf-8')
    return notify_type, pseudo

# Transport
def encode_data(data: bytes) -> bytes:
    """C <-> S : DATA"""
    return data

def decode_data(payload: bytes) -> bytes:
    return payload

# Error
def encode_error(err_code: int, message: str) -> bytes:
    """S -> C : ERROR"""
    msg_bytes = message.encode('utf-8')
    return struct.pack('B', err_code) + msg_bytes

def decode_error(payload: bytes) -> Tuple[int, str]:
    if len(payload) < 1:
        raise ProtocolError("Error payload too short")
    err_code = payload[0]
    message = payload[1:].decode('utf-8')
    return err_code, message

