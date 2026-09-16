import json
import socket
import uuid

try:
    from .player import Player
except ImportError:
    from player import Player


class GameClient:
    def __init__(self, server_address, name):
        self.server_address = server_address
        self.connection = None
        self.player = Player(name=name, id=uuid.uuid4())

    def connect(self):
        host, port = self.server_address.rsplit(":", 1)
        self.connection = socket.create_connection((host, int(port)))
        print(f"Connected to game server at {self.server_address}")
        self.send_data(self.player.to_dict())

    def send_data(self, data):
        if self.connection is None:
            raise ConnectionError("Client is not connected")
        message = json.dumps(data).encode("utf-8") + b"\n"
        self.connection.sendall(message)

    def receive_data(self):
        if self.connection is None:
            raise ConnectionError("Client is not connected")
        return json.loads(self.connection.recv(4096).decode("utf-8"))

    def status(self):
        self.send_data({"command": "status"})
        return self.receive_data()

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def process_command(self, command):
        command = command.strip().lower()
        if command in ("stat", "st", "status"):
            response = self.status()
            print(f"Submarine position: {tuple(response['sub_location'])}")
            return True
        return command != "quit"

def main():
    server_address = "localhost:8080"
    player_name = input("Enter your name: ").strip()
    client = GameClient(server_address, player_name)

    try:
        client.connect()
        while True:
            if not client.process_command(input("> ")):
                break
    except KeyboardInterrupt:
        print("Disconnecting from game server")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()