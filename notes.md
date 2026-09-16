 ## start game server
 python game_server.py
 Set-Location 'D:\site\sub_hunt'; py -3 .\game_server.py

 ## start and stop clients
 py -3 -c "import socket; connection1 = socket.create_connection(('localhost', 8080), timeout=2); connection2 = socket.create_connection(('localhost', 8080), timeout=2); connection2.close(); connection1.close()"
 
 Set-Location 'D:\site\sub_hunt'; py -3 .\game_client.py