import unittest
import sys
import os
import struct

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from protocol import (
    OpCode, ProtocolError, RoomInfo,
    encode_message, decode_header, decode_packet,
    encode_login_req, decode_login_req,
    encode_login_resp, decode_login_resp,
    encode_room_list, decode_room_list,
    encode_join_req, decode_join_req,
    encode_room_resp, decode_room_resp,
    encode_notify, decode_notify,
    encode_error, decode_error,
    encode_leave_req, encode_data, decode_data
)

class TestProtocol(unittest.TestCase):
    
    def test_header_and_packet_framing(self):
        # Test generic message construction
        payload = b'\x01\x02\x03'
        opcode = OpCode.REQ_LOGIN # Just using an opcode
        
        # Encode
        full_msg = encode_message(opcode, payload)
        
        # Check size
        # Size = 1 (OpCode) + 3 (Payload) = 4
        # Header = 4 bytes BE of 4 -> 00 00 00 04
        # Body = 01 (OpCode) + 01 02 03
        expected_size = 4
        expected_header = b'\x00\x00\x00\x04'
        self.assertEqual(full_msg[:4], expected_header)
        self.assertEqual(full_msg[4], 1) # OpCode
        self.assertEqual(full_msg[5:], payload)
        
        # Decode Header
        size = decode_header(full_msg[:4])
        self.assertEqual(size, 4)
        
        # Decode Packet
        decoded_op, decoded_payload = decode_packet(full_msg[4:])
        self.assertEqual(decoded_op, opcode)
        self.assertEqual(decoded_payload, payload)

    def test_login(self):
        pseudo = "Alice"
        encoded = encode_login_req(pseudo)
        decoded = decode_login_req(encoded)
        self.assertEqual(decoded, pseudo)
        
        status = 0
        encoded_resp = encode_login_resp(status)
        decoded_resp = decode_login_resp(encoded_resp)
        self.assertEqual(decoded_resp, 0)
        
    def test_room_list(self):
        rooms = [
            RoomInfo(room_id=1, name="Room A", players=2, max_players=4),
            RoomInfo(room_id=1024, name="Room B", players=0, max_players=8)
        ]
        
        encoded = encode_room_list(rooms)
        
        # Manual check of encoded bytes for first room
        # [NbRooms=2]
        self.assertEqual(encoded[0], 2)
        # Room A: ID(1)=00000001, LenName(6), "Room A", P(2), M(4)
        offset = 1
        self.assertEqual(encoded[offset:offset+4], b'\x00\x00\x00\x01')
        offset += 4
        self.assertEqual(encoded[offset], 6)
        offset += 1
        self.assertEqual(encoded[offset:offset+6], b'Room A')
        offset += 6
        self.assertEqual(encoded[offset], 2)
        self.assertEqual(encoded[offset+1], 4)
        
        decoded = decode_room_list(encoded)
        self.assertEqual(len(decoded), 2)
        self.assertEqual(decoded[0].name, "Room A")
        self.assertEqual(decoded[1].room_id, 1024)

    def test_join_room(self):
        rid = 123456
        encoded = encode_join_req(rid)
        self.assertEqual(encoded, b'\x00\x01\xe2\x40') # 123456 in hex is 1E240
        decoded = decode_join_req(encoded)
        self.assertEqual(decoded, rid)

    def test_room_resp(self):
        players = ["Alice", "Bob"]
        encoded = encode_room_resp(players)
        decoded = decode_room_resp(encoded)
        self.assertEqual(decoded, players)

    def test_notify(self):
        # Type 0x00 (JOIN), Pseudo "Bob"
        encoded = encode_notify(0x00, "Bob")
        # Payload: Type(1) + Len(1) + Pseudo
        self.assertEqual(encoded[0], 0x00)
        self.assertEqual(encoded[1], 3)
        self.assertEqual(encoded[2:], b'Bob')
        
        t, p = decode_notify(encoded)
        self.assertEqual(t, 0x00)
        self.assertEqual(p, "Bob")

    def test_error(self):
        code = 0xFF
        msg = "Fatal Error"
        encoded = encode_error(code, msg)
        c, m = decode_error(encoded)
        self.assertEqual(c, code)
        self.assertEqual(m, msg)

if __name__ == '__main__':
    unittest.main()
