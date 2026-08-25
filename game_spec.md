This spec describes the game sub_hunt.

# Overview
sub_hunt is a text based game where two players drive submarines and try to hunt each other down. 
* Your submarine can survive one torpedo hit. The second will destroy it.
* Your sub moves one map tile per turn.

# Player Actions
* Map - View the map, including the last known positions of any other players.
* Move - Move your submarine to a new a tile in the map grid. You may move once per turn.
* Fire - Fire a torpedo at a specific map grid. You can fire two torpedoes per turn. Firing gives away your location. The torpedo will detonate on your next turn.
* End turn - Allows the next player to take a turn. Ending your turn before moving means your sub has stopped moving.
* Ping - Perform a sonar ping that will uncover the locations of any other subs. Will also give away your location.
* Quit - Removes the player from the game.

# Notifications
* Proximity - Another sub is within 3 tiles on the map grid.
* Incoming torpedo - includes the location of the sub that fired it.
* Submarine explosion - your torpedo destroys a sub.
* Submarine hit - your torpedo damages a sub.

# Future features
* advanced moves to avoid torpedoes.
* launch decoys to distract torpedoes.
* handle sub heading and speed. Make possible turns dependent on it.
* torpedo lock on.
