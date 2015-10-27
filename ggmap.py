# Data structure for the playing grid that the game takes place on.
import pygame
import ggparty

# Enums/Constants
#  -- Mouse Buttons
MOUSE_LEFT = 1
MOUSE_RIGHT = 3

class MapGrid():

	#TODO: We need a data structure for holding all the parties that are on the map grid.
	#	   This includes a way to tell which party is controlled by the player, which is controlled by the AI, etc.
	#		We also need a data structure to track the movement sequence the player is currently inputting.
	#		We need a way to track the health of each of the players.
	#		We need a way to distinguish between the simulation phase and the input phase.
	#			(More specifically: Player input phase, AI input phase, Simulation phase)

	def __init__(self, width, height):
		# This sets the WIDTH and HEIGHT of each grid location and the MARGIN between each cell
		self.WIDTH = width
		self.HEIGHT = height
		self.MARGIN = 5

		self.grid = [[0 for row in range(10)] for column in range(10)]

	def update(self, event):
		#TODO: handling of keyboard input, mouse clicks, etc for the map scene.
		# Particuarly, inputting the movement sequences, and clicking the buttons to go to the simulation phase.
		todo = 0

	#party: ggparty.PartyGrid() object
	def addPartyToMap(self, party, gridx, gridy):
		#TODO: add a party onto the map grid at the given position
		todo = 0

	def getParty(self, gridx, gridy):
		#TODO: Return the party located at (gridx, gridy) on the map, or -1 if no party is located at that position.
		todo = 0
		return -1

	def moveParty(self, sourcex, sourcey, destx, desty):
		#TODO: Move the party located at (sourcex, sourcey) to (destx, desty)
		#Alternately, you can implement functions for moving up/left/down/right by one grid cell
		todo = 0

	def removeParty(self, gridx, gridy):
		#TODO: Remove the party located at (gridx, gridy) from the map.
		todo = 0

	#Rotate the party located at (gridx, gridy). The angle should be ggparty.UP, ggparty.DOWN, ggparty.LEFT, or ggparty.RIGHT.
	def rotateParty(self, gridx, gridy, angle):
		party = getParty(gridx, gridy)
		if party != -1:
			for _ in range(4):
				if party.grid_angle == angle:
					break
				else:
					party.rotatePartyClockwise()

	def simulateShoot(self):
		#TODO: Check if any of the party members are capable of shooting characters in other player's parties
		todo = 0

	# Renders the map on screen
	def renderGrid(self, screen):
		# Draw the grid
		for row in range(10):
			for column in range(10):
				color = (255,255,255)
				pygame.draw.rect(screen, color, [(self.MARGIN + self.WIDTH) * column + self.MARGIN, (self.MARGIN + self.HEIGHT) * row + self.MARGIN, self.WIDTH, self.HEIGHT])
