import json
import select
import socket

try:
    from .player import Player
except ImportError:
    from player import Player


class GameServer:
    def __init__(self):
        self.players = {}
        self.game_state = {}
        self.connections = []
        self.connection_players = {}

    def add_player(self, player):
        self.players[player.id] = player
        self.game_state[player.id] = {}

    def remove_player(self, player):
        self.players.pop(player.id, None)
        self.game_state.pop(player.id, None)

    def update_game_state(self, player: Player, new_state):
        if player.id in self.game_state:
            self.game_state[player.id] = new_state

    def get_game_state(self):
        return self.game_state

    def handle_command(self, player: Player, command):
        if command == "status" and player.id in self.game_state:
            return {"command": "status", "sub_location": list(player.sub_location)}
        return {"error": "Unknown command"}

    def send_response(self, connection, response):
        connection.sendall(json.dumps(response).encode("utf-8") + b"\n")

    def disconnect_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)
        player = self.connection_players.pop(connection, None)
        if player is not None:
            self.remove_player(player)
        connection.close()

    def process_connection_data(self, connection, data):
        if not data:
            self.disconnect_connection(connection)
            return False

        message = json.loads(data.decode("utf-8").strip())
        if "command" in message:
            player = self.connection_players.get(connection)
            if player is None:
                response = {"error": "Player is not connected"}
            else:
                response = self.handle_command(
                    player=player,
                    command=message["command"],
                )
            self.send_response(connection, response)
        else:
            player = Player.from_dict(message)
            self.add_player(player)
            self.connection_players[connection] = player
            print(f"Player joined: {player.name} ({player.id})")
        return True

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
                        server.disconnect_connection(connection)
                        continue

                    server.process_connection_data(connection, data)
        except KeyboardInterrupt:
            print("Shutting down game server")
        finally:
            for connection in list(server.connections):
                print(f"Disconnecting client {connection.getpeername()}")
                server.disconnect_connection(connection)


if __name__ == "__main__":
    main()