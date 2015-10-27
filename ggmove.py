# Data structure representation of a move and/or sequence of moves. 
# Whether we need both of these data structures or just one is up for consideration.
class Move():
	def __init__(self):
		# ...
		nothing = 0
	
	def oneStep(self, ploc, cmds, GRID_SIZE):
		# ***************************** NEED FACING HERE ******************
		# Takes the player locations and the commands from each player
		# Computes the player locations after each command and outputs new player locations
		for player in range(len(cmds)): # For each player
			if cmds[player] == "UP": # Execute the appropriate command
				ploc[player][1] -= 1 # Modify location for that player
			elif cmds[player] == "DOWN":
				ploc[player][1] += 1
			elif cmds[player] == "RIGHT":
				ploc[player][0] += 1
			elif cmds[player] == "LEFT":
				ploc[player][0] -= 1
			# Make sure player is still on the map
			ploc[player][1] = max(ploc[player][1],0) # Bottom boundary
			ploc[player][1] = min(ploc[player][1],GRID_SIZE-1) # Top boundary
			ploc[player][0] = max(ploc[player][0],0) # Left boundary
			ploc[player][0] = min(ploc[player][0],GRID_SIZE-1) # Right boundary
		return ploc

#class MoveSequence():
#	def __init__(self):
#		# ...
