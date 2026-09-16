import socket
import unittest
from typing import cast
from unittest.mock import patch

from src.game_client import GameClient


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

    def test_process_command_handles_status_aliases(self):
        client = GameClient("localhost:8080", "Test Player")

        with patch.object(
            client,
            "status",
            return_value={"sub_location": [4, 9]},
        ) as status:
            self.assertTrue(client.process_command(" stat "))
            self.assertTrue(client.process_command("st"))
            self.assertTrue(client.process_command("STATUS"))

        self.assertEqual(status.call_count, 3)

    def test_process_command_stops_on_quit(self):
        client = GameClient("localhost:8080", "Test Player")

        self.assertFalse(client.process_command(" quit "))
        self.assertTrue(client.process_command("unknown"))


if __name__ == "__main__":
    unittest.main()