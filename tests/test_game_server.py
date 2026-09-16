import json
import unittest
import uuid

from src.game_server import GameServer
from src.player import Player


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

    def test_process_connection_data_registers_player(self):
        connection = FakeConnection()
        self.server.connections.append(connection)
        message = json.dumps(self.player.to_dict()).encode("utf-8")

        self.assertTrue(self.server.process_connection_data(connection, message))

        self.assertEqual(self.server.connection_players[connection], self.player)
        self.assertEqual(self.server.players[self.player.id], self.player)

    def test_process_connection_data_handles_status_for_registered_player(self):
        connection = FakeConnection()
        self.server.connection_players[connection] = self.player
        self.server.add_player(self.player)

        message = b'{"command": "status"}'
        self.assertTrue(self.server.process_connection_data(connection, message))

        self.assertEqual(
            json.loads(connection.sent[0].decode("utf-8")),
            {
                "command": "status",
                "sub_location": [4, 9],
            },
        )

    def test_process_connection_data_rejects_unregistered_command(self):
        connection = FakeConnection()

        self.server.process_connection_data(connection, b'{"command": "status"}')

        self.assertEqual(
            json.loads(connection.sent[0].decode("utf-8")),
            {"error": "Player is not connected"},
        )

    def test_process_connection_data_disconnects_player(self):
        connection = FakeConnection()
        self.server.connections.append(connection)
        self.server.connection_players[connection] = self.player
        self.server.add_player(self.player)

        self.assertFalse(self.server.process_connection_data(connection, b""))

        self.assertNotIn(connection, self.server.connections)
        self.assertNotIn(connection, self.server.connection_players)
        self.assertNotIn(self.player.id, self.server.players)
        self.assertTrue(connection.closed)


if __name__ == "__main__":
    unittest.main()