import json
import socket
import unittest
import uuid
from typing import cast

from game_client import GameClient
from game_server import GameServer
from player import Player


class FakeConnection:
    def __init__(self, received=b''):
        self.received = received
        self.sent = []
        self.closed = False

    def sendall(self, data):
        self.sent.append(data)

    def recv(self, size):
        return self.received

    def close(self):
        self.closed = True


class GameClientTests(unittest.TestCase):
    def test_status_sends_status_command_and_reads_response(self):
        connection = FakeConnection(b'{"command": "status"}')
        client = GameClient("localhost:8080", "Test Player")
        client.connection = cast(socket.socket, connection)

        response = client.status()

        self.assertEqual(response, {"command": "status"})
        self.assertEqual(
            connection.sent,
            [b'{"command": "status"}\n'],
        )

    def test_disconnect_closes_connection(self):
        connection = FakeConnection()
        client = GameClient("localhost:8080", "Test Player")
        client.connection = cast(socket.socket, connection)

        client.disconnect()

        self.assertTrue(connection.closed)
        self.assertIsNone(client.connection)


class GameServerTests(unittest.TestCase):
    def setUp(self):
        self.server = GameServer()
        self.player = Player(
            name="Test Player",
            id=uuid.UUID("12345678-1234-5678-1234-567812345678"),
            sub_location=(4, 9),
        )

    def test_add_update_and_remove_player(self):
        self.server.add_player(self.player)
        self.assertIs(self.server.players[self.player.id], self.player)
        self.assertEqual(self.server.get_game_state(), {self.player.id: {}})

        new_state = {"ready": True}
        self.server.update_game_state(self.player, new_state)
        self.assertEqual(self.server.game_state[self.player.id], new_state)

        self.server.remove_player(self.player)
        self.assertNotIn(self.player.id, self.server.players)
        self.assertNotIn(self.player.id, self.server.game_state)

    def test_status_command_returns_player_position(self):
        self.server.add_player(self.player)

        response = self.server.handle_command(self.player, "status")

        self.assertEqual(
            response,
            {
                "command": "status",
                "sub_location": [4, 9],
            },
        )

    def test_server_rejects_stat_command(self):
        self.server.add_player(self.player)

        response = self.server.handle_command(self.player, "stat")

        self.assertEqual(response, {"error": "Unknown command"})

    def test_send_response_serializes_json_with_newline(self):
        connection = FakeConnection()

        self.server.send_response(connection, {"command": "status"})

        self.assertEqual(
            json.loads(connection.sent[0].decode("utf-8")),
            {"command": "status"},
        )
        self.assertTrue(connection.sent[0].endswith(b"\n"))


if __name__ == "__main__":
    unittest.main()