# Data structure representation of a move and/or sequence of moves. 
# Whether we need both of these data structures or just one is up for consideration.
import ggparty
import ggmap
import pygame

def setRotation(player, direction):
	diff = player.grid_angle - direction
	diff = diff % 360 # correct negative angles
	while diff > 0:
		player.rotatePartyClockwise()
		diff -= 90	
	player.resizeGrid(ggmap.WIDTH, ggmap.HEIGHT, ggmap.MARGIN)

# Set the party to be at a specific location on the supergrid, facing a specific angle
def setAbsolute(player, location, direction):
	setRotation(player, direction)
	player.supergrid_location[0] = min(max(location[0],0), ggmap.GRID_SIZE-3)
	player.supergrid_location[1] = min(max(location[1],0), ggmap.GRID_SIZE-3)


class Move():
	def __init__(self):
		self.damage = 5
		# Initialize graphics
		self.explosion = pygame.image.load('explosion.jpg')
		self.explosion = pygame.transform.scale(self.explosion, (ggmap.WIDTH, ggmap.HEIGHT))	
	
	def oneStep(self, player, cmd):
		# Takes the player locations and the commands from each player
		# Computes the player locations after each command and outputs new player locations
		if player.alive == 0: # if the player is dead, don't accept move commands
			return
		if cmd == ggparty.UP: # Execute the appropriate command
			player.supergrid_location[0] = max(player.supergrid_location[0]-1,0)
			setRotation(player, ggparty.UP)
		elif cmd == ggparty.DOWN:
			player.supergrid_location[0] = min(player.supergrid_location[0]+1,ggmap.GRID_SIZE-3)
			setRotation(player, ggparty.DOWN)			
		elif cmd == ggparty.RIGHT:
			player.supergrid_location[1] = min(player.supergrid_location[1]+1,ggmap.GRID_SIZE-3)
			setRotation(player, ggparty.RIGHT)
		elif cmd == ggparty.LEFT:
			player.supergrid_location[1] = max(player.supergrid_location[1]-1,0)
			setRotation(player, ggparty.LEFT)
	
	def drawAttack(self, atkloc, tarloc, screen):
		color = ggmap.RED
		# draw beam between attacker and defender
		pygame.draw.rect(screen,
					color,
					[(ggmap.MARGIN + ggmap.WIDTH) * atkloc[1] + ggmap.MARGIN + ggmap.WIDTH/2,
					(ggmap.MARGIN + ggmap.HEIGHT) * atkloc[0] + ggmap.MARGIN + ggmap.HEIGHT/2,
					(ggmap.MARGIN + ggmap.WIDTH) * (tarloc[1] - atkloc[1]),
					(ggmap.MARGIN + ggmap.HEIGHT) * (tarloc[0] - atkloc[0])])
		# draw explosion on defender
		screen.blit(self.explosion,((ggmap.MARGIN + ggmap.WIDTH) * tarloc[1] + ggmap.MARGIN,
				(ggmap.MARGIN + ggmap.HEIGHT) * tarloc[0] + ggmap.MARGIN))
	
	def attack(self, attackingPlayer, huPlayer, aiPlayers, screen):
		# Takes the player locations and facing and checks to see if there are any valid attacks
		# If there are valid attacks, resolve them
		
		# if screen == 0, don't draw anything
		
		allPlayers = aiPlayers + [huPlayer]
		allOccupied = [(player.getSupergridCells(), player) for player in allPlayers if player != attackingPlayer]

		for attacker in range(2):
			if attackingPlayer.party_members[attacker].chartype == ggparty.SINGLE_SHOT:
				for targets in allOccupied:
					for tarloc in targets[0]:
						match_horz = False
						match_vert = False
						element_facing = attackingPlayer.party_members[attacker].rotation
						atkloc = (attackingPlayer.party_positions[attacker][1]+attackingPlayer.supergrid_location[0]
							, attackingPlayer.party_positions[attacker][0]+attackingPlayer.supergrid_location[1])
						if element_facing == ggparty.UP:
							match_horz = tarloc[1] == atkloc[1]
							match_vert = tarloc[0] <= atkloc[0]
						elif element_facing == ggparty.DOWN:
							match_horz = tarloc[1] == atkloc[1]
							match_vert = tarloc[0] >= atkloc[0]
						elif element_facing == ggparty.RIGHT:
							match_horz = tarloc[1] >= atkloc[1]
							match_vert = tarloc[0] == atkloc[0]
						elif element_facing == ggparty.LEFT:
							match_horz = tarloc[1] <= atkloc[1]
							match_vert = tarloc[0] == atkloc[0]
						if match_horz & match_vert:
							targets[1].health -= self.damage
							if screen != 0:
								self.drawAttack(atkloc, tarloc, screen)
						
			elif attackingPlayer.party_members[attacker].chartype == ggparty.DOUBLE_SHOT:
				for targets in allOccupied:
					for tarloc in targets[0]:
						match = False
						element_facing = attackingPlayer.party_members[attacker].rotation
						atkloc = (attackingPlayer.party_positions[attacker][1]+attackingPlayer.supergrid_location[0]
							, attackingPlayer.party_positions[attacker][0]+attackingPlayer.supergrid_location[1])
						if element_facing == ggparty.UP:
							match = tarloc[1] == atkloc[1]
						elif element_facing == ggparty.DOWN:
							match = tarloc[1] == atkloc[1]
						elif element_facing == ggparty.RIGHT:
							match = tarloc[0] == atkloc[0]
						elif element_facing == ggparty.LEFT:
							match = tarloc[0] == atkloc[0]
						if match:
							targets[1].health -= self.damage
							if screen != 0:
								self.drawAttack(atkloc, tarloc, screen)