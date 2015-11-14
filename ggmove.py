# Data structure representation of a move and/or sequence of moves. 
# Whether we need both of these data structures or just one is up for consideration.
import ggparty
import ggmap
import pygame

class Move():
	def __init__(self):
		# ...
		self.damage = 5
		# Initialize graphics
		self.explosion = pygame.image.load('explosion.jpg')
		self.explosion = pygame.transform.scale(self.explosion, (ggmap.WIDTH, ggmap.HEIGHT))

# RIGHT = 0
# UP = 90
# LEFT = 180
# DOWN = 270		

	def setRotation(self, player, direction):
		diff = player.grid_angle - direction
		diff = diff % 360 # correct negative angles
		while diff > 0:
			player.rotatePartyClockwise()
			diff -= 90
		player.resizeGrid(ggmap.WIDTH, ggmap.HEIGHT, ggmap.MARGIN)
	
	def oneStep(self, player, cmd):
		# Takes the player locations and the commands from each player
		# Computes the player locations after each command and outputs new player locations
		if player.alive == 0: # if the player is dead, don't accept move commands
			return
		if cmd == "UP": # Execute the appropriate command
			player.supergrid_location[0] -= 1 # Modify location for that player
			self.setRotation(player, ggparty.UP)
		elif cmd == "DOWN":
			player.supergrid_location[0] += 1
			self.setRotation(player, ggparty.DOWN)
		elif cmd == "RIGHT":
			player.supergrid_location[1] += 1
			self.setRotation(player, ggparty.RIGHT)
		elif cmd == "LEFT":
			player.supergrid_location[1] -= 1
			self.setRotation(player, ggparty.LEFT)
		# Make sure player is still on the map
		player.supergrid_location[1] = max(player.supergrid_location[1],0) # Bottom boundary
		player.supergrid_location[1] = min(player.supergrid_location[1],ggmap.GRID_SIZE-3) # Top boundary
		player.supergrid_location[0] = max(player.supergrid_location[0],0) # Left boundary
		player.supergrid_location[0] = min(player.supergrid_location[0],ggmap.GRID_SIZE-3) # Right boundary
	
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
		
		allPlayers = aiPlayers + [huPlayer]
		match_horz = False
		match_vert = False
		
		for attacker in range(2):
			if attackingPlayer.party_members[attacker].chartype == 0:
				for targetPlayer in allPlayers:
					for target in range(2):
						atkloc = [sum(x) for x in zip(attackingPlayer.supergrid_location, attackingPlayer.party_positions[attacker])]
						tarloc = [sum(x) for x in zip(targetPlayer.supergrid_location, targetPlayer.party_positions[attacker])]
						element_facing = (attackingPlayer.party_members[attacker].facing + attackingPlayer.grid_angle) % 360
						if attackingPlayer == targetPlayer: # Don't shoot yourself
							pass
						elif element_facing == ggparty.UP:
							match_horz = tarloc[0] == atkloc[0]
							match_vert = tarloc[1] <= atkloc[1]
						elif element_facing == ggparty.DOWN:
							match_horz = tarloc[0] == atkloc[0]
							match_vert = tarloc[1] >= atkloc[1]
						elif element_facing == ggparty.RIGHT:
							match_horz = tarloc[0] >= atkloc[0]
							match_vert = tarloc[1] == atkloc[1]
						elif element_facing == ggparty.LEFT:
							match_horz = tarloc[0] <= atkloc[0]
							match_vert = tarloc[1] == atkloc[1]
						if match_horz & match_vert:
							print element_facing
							targetPlayer.health -= self.damage
							self.drawAttack(atkloc, tarloc, screen)
						match_horz = False
						match_vert = False
						
			elif attackingPlayer.party_members[attacker].chartype == 1:
				for targetPlayer in allPlayers:
					for target in range(2):
						atkloc = [sum(x) for x in zip(attackingPlayer.supergrid_location, attackingPlayer.party_positions[attacker])]
						tarloc = [sum(x) for x in zip(targetPlayer.supergrid_location, targetPlayer.party_positions[attacker])]
						element_facing = attackingPlayer.party_members[attacker].facing + attackingPlayer.grid_angle % 360
						if attackingPlayer == targetPlayer: # Don't shoot yourself
							pass
						elif element_facing == ggparty.UP:
							match_horz = tarloc[0] == atkloc[0]
							match_vert = True
						elif element_facing == ggparty.DOWN:
							match_horz = tarloc[0] == atkloc[0]
							match_vert = True
						elif element_facing == ggparty.RIGHT:
							match_horz = True
							match_vert = tarloc[1] == atkloc[1]
						elif element_facing == ggparty.LEFT:
							match_horz = True
							match_vert = tarloc[1] == atkloc[1]
						if match_horz & match_vert:
							print element_facing
							targetPlayer.health -= self.damage
							self.drawAttack(atkloc, tarloc, screen)
						match_horz = False
						match_vert = False