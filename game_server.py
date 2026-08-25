import json
import select
import socket

from player import Player


class GameServer:
    def __init__(self):
        self.players = []
        self.game_state = {}
        self.connections = []

    def add_player(self, player):
        self.players.append(player)
        self.game_state[player.id] = {}

    def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)
            del self.game_state[player.id]

    def update_game_state(self, player_id, new_state):
        if player_id in self.game_state:
            self.game_state[player_id] = new_state

    def get_game_state(self):
        return self.game_state

def main():
    server = GameServer()
    host = "localhost"
    port = 8080

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((host, port))
        listener.listen()
        listener.settimeout(1.0)
        print(f"Game server listening on {host}:{port}")

        try:
            while True:
                readable, _, _ = select.select(
                    [listener, *server.connections], [], [], 1.0
                )

                if listener in readable:
                    connection, address = listener.accept()
                    server.connections.append(connection)
                    print(f"Client connected from {address}")

                for connection in readable:
                    if connection is listener:
                        continue
                    data = connection.recv(4096)
                    if not data:
                        print(f"Client disconnected from {connection.getpeername()}")
                        server.connections.remove(connection)
                        connection.close()
                        continue

                    message = json.loads(data.decode("utf-8").strip())
                    player = Player.from_dict(message)
                    server.add_player(player)
                    print(f"Player joined: {player.name} ({player.id})")
        except KeyboardInterrupt:
            print("Shutting down game server")
        finally:
            for connection in server.connections:
                print(f"Disconnecting client {connection.getpeername()}")
                connection.close()


if __name__ == "__main__":
    main()