import json
import select
import socket

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
        if command == "stat" and player.id in self.game_state:
            return {"command": "stat", "sub_location": list(player.sub_location)}
        return {"error": "Unknown command"}

    def send_response(self, connection, response):
        connection.sendall(json.dumps(response).encode("utf-8") + b"\n")

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
                        player = server.connection_players.pop(connection, None)
                        if player is not None:
                            server.remove_player(player)
                        connection.close()
                        continue

                    message = json.loads(data.decode("utf-8").strip())
                    if "command" in message:
                        player = server.connection_players.get(connection)
                        if player is None:
                            response = {"error": "Player is not connected"}
                        else:
                            response = server.handle_command(
                                player=player,
                                command=message["command"],
                            )
                        server.send_response(connection, response)
                    else:
                        player = Player.from_dict(message)
                        server.add_player(player)
                        server.connection_players[connection] = player
                        print(f"Player joined: {player.name} ({player.id})")
        except KeyboardInterrupt:
            print("Shutting down game server")
        finally:
            for connection in server.connections:
                print(f"Disconnecting client {connection.getpeername()}")
                player = server.connection_players.pop(connection, None)
                if player is not None:
                    server.remove_player(player)
                connection.close()


if __name__ == "__main__":
    main()