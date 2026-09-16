 ## start game server
 python -m src.game_server
 Set-Location 'D:\site\sub_hunt'; py -3 -m src.game_server

 ## start and stop clients
 py -3 -c "import socket; connection1 = socket.create_connection(('localhost', 8080), timeout=2); connection2 = socket.create_connection(('localhost', 8080), timeout=2); connection2.close(); connection1.close()"
 
 Set-Location 'D:\site\sub_hunt'; py -3 -m src.game_client