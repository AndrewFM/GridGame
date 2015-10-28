# Data structure representation of a move and/or sequence of moves. 
# Whether we need both of these data structures or just one is up for consideration.
class Move():
	def __init__(self):
		# ...
		nothing = 0
	
	def oneStep(self, ploc, facing, status, cmds, GRID_SIZE):
		# Takes the player locations and the commands from each player
		# Computes the player locations after each command and outputs new player locations
		for player in range(len(cmds)): # For each player
			if status[player] >= 0:
				if cmds[player] == "UP": # Execute the appropriate command
					ploc[player][1] -= 1 # Modify location for that player
					facing[player] = 90.0
				elif cmds[player] == "DOWN":
					ploc[player][1] += 1
					facing[player] = 270.0
				elif cmds[player] == "RIGHT":
					ploc[player][0] += 1
					facing[player] = 0.0
				elif cmds[player] == "LEFT":
					ploc[player][0] -= 1
					facing[player] = 180.0
				# Make sure player is still on the map
				ploc[player][1] = max(ploc[player][1],0) # Bottom boundary
				ploc[player][1] = min(ploc[player][1],GRID_SIZE-1) # Top boundary
				ploc[player][0] = max(ploc[player][0],0) # Left boundary
				ploc[player][0] = min(ploc[player][0],GRID_SIZE-1) # Right boundary
		return ploc, facing
	
	def attack(self, ploc, facing, health):
		# Takes the player locations and facing and checks to see if there are any valid attacks
		# If there are valid attacks, resolve them
		atklocs = []
		for attacker in range(len(health)):
			for target in range(len(health)):
				# Check to see if the attacker hits anyone
				match_horz = 0 # default to miss
				match_vert = 0
				if attacker == target: # Don't shoot yourself
					pass
				elif facing[attacker] == 90: # Up
					match_horz = ploc[target][0] == ploc[attacker][0]
					match_vert = ploc[target][1] <= ploc[attacker][1]
				elif facing[attacker] == 270: # Down
					match_horz = ploc[target][0] == ploc[attacker][0]
					match_vert = ploc[target][1] >= ploc[attacker][1]
				elif facing[attacker] == 0: # Right
					match_horz = ploc[target][0] >= ploc[attacker][0]
					match_vert = ploc[target][1] == ploc[attacker][1]
				elif facing[attacker] == 180: # Left
					match_horz = ploc[target][0] <= ploc[attacker][0]
					match_vert = ploc[target][1] == ploc[attacker][1]
				
				# If there's a target there, do damage to it
				if match_horz and match_vert:
					health[target] -= 20
					atklocs += [[ploc[attacker],ploc[target]]]
		return health, atklocs
					
				

#class MoveSequence():
#	def __init__(self):
#		# ...
