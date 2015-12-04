import pygame
import math
import numpy as np
import copy
import ggmove
import ggparty

# Enums/Constants
#  -- Character Types
SINGLE_SHOT = 0 	# 1x1 character that can shoot in a single direction
DOUBLE_SHOT = 1     # 1x2 character that can shoot in two directions
SHIELD = 2          # 2x2 character that cannot shoot at all
#  -- Rotation Directions
RIGHT = 0
UP = 90
LEFT = 180
DOWN = 270
#  -- Grid Attributes
GRID_SIZE = 3  # In number of cells
CELL_SIZE = 32 # In pixels
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
#gridColor = BLACK
GRID_ARROW_SIZE = 16 # In pixels

# Representation of a single character within a party.
class CharacterSprite(pygame.sprite.Sprite):
	# position: 	(x,y) tuple
	#    angle: 	angle, from the rotation enum list
	# chartype:     value from the character enum list
	#    ghost:		Is this an actual character, or a preview image?
	def __init__(self, position, angle, chartype, ghost):
		pygame.sprite.Sprite.__init__(self)
		self.ghost = ghost
		if ghost == 0:
			self.src_image = pygame.image.load("img/char_"+str(chartype)+".png")
		else:
			self.src_image = pygame.image.load("img/char_trans_"+str(chartype)+".png")
		self.chartype = chartype
		self.rotate(angle)
		self.rect = self.image.get_rect()
		self.rect.topleft = position
		self.facing = [] # This needs to mean something.

	def rotate(self, angle):
		self.rotation = angle
		self.image = pygame.transform.rotate(self.src_image, angle)
			
	def scale(self, cellWidth, cellHeight, margin):
		dimensions = pygame.Surface.get_size(self.image)
		source_dimensions = pygame.Surface.get_size(self.src_image)
		if self.chartype == 0:	# 1x1
			shapeWidth = cellWidth
			shapeHeight = cellHeight
		elif self.chartype == 2: # 2x2
			shapeWidth = cellWidth*2 + margin
			shapeHeight = cellHeight*2 + margin
		elif dimensions[0] < dimensions [1]: # 1x2, has two different facings. First, vertical.
			shapeWidth = cellWidth
			shapeHeight = cellHeight*2 + margin
		else: # now, horizontal
			shapeWidth = cellWidth*2 + margin
			shapeHeight = cellHeight			
		self.image = pygame.transform.scale(self.image, (int(shapeWidth), int(shapeHeight)))

	#Increment the current rotation by some amount
	def rotateRelative(self, angle):
		newdegrees = (self.rotation + angle) % 360
		self.rotate(newdegrees)

# Data Structure for 3x3 Character Parties
class PartyGrid():

	def __init__(self):
		self.ai_control = 0		   # Set to 0 if human controlled, set to an ggai.AIOpponent object if AI controlled.
		self.grid_position = (0,0)
		self.supergrid_location = [0,0]
		self.grid_angle = RIGHT	   # Facing direction of the entire party grid as a whole
		self.party_members = []    # Contains CharacterSprite elements. Must be in parallel with array below.
		self.party_positions = []  # Contains (gridx, gridy) elements. Must be in parallel with array above.
		self.grid_contents = [[(0,0,-1) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)] # Contains Character enum elements & grid pos of source character.
		self.grid_color = BLACK
		self.health = []
		self.facing_indicator = 1
		self.cmd_seq = ["[empty]","[empty]","[empty]"]
		self.cmd_id = 0
		self.alive = 1
		# Hardcoding the global rotation translations for the 1x2 character for now
		# ... because I'm not totally sure how to do it programatically
		self.double_posmapUD = [ #Up/Down to Left/Right
			[(1,0),(1,1),(1,2)],
			[(0,0),(0,1),(0,2)]
		]
		self.double_posmapLR = [ #Left/Right to Up/Down
			[(2,0),(2,1),(-1,-1)],
			[(1,0),(1,1),(-1,-1)],
			[(0,0),(0,1),(-1,-1)]
		]

	# Assign an AI controller to this party
	def assignAI(self, aiobject):
		self.ai_control = aiobject

	# Is this party AI controller or not?
	def isAI(self):
		if self.ai_control == 0:
			return 0
		else:
			return 1

	# Returns the local coordinates of all occupied cells
	def getOccupiedCells(self):
		coordList = []
		for i in range(self.numberOfCharacters()):
			member = self.party_members[i]
			pos = self.party_positions[i]
			for coord in self.__determineOccupyingCells(member.chartype, member.rotation, pos[0], pos[1]):
				coordList.append((coord[1],coord[0]))
		return coordList

	# Returns the global coordinates of all occupied cells
	def getSupergridCells(self):
		coordList = []
		for i in range(self.numberOfCharacters()):
			member = self.party_members[i]
			pos = self.party_positions[i]
			for coord in self.__determineOccupyingCells(member.chartype, member.rotation, pos[0], pos[1]):
				coordList.append((coord[1]+self.supergrid_location[0],coord[0]+self.supergrid_location[1]))
		return coordList		
		
	# Returns 1 if the character was successfully inserted, 0 otherwise.
	# Angles should be in degrees, should be between 0 and 2pi, and should always be multiples of pi/2.
	def appendCharacter(self, chartype, angle, gridx, gridy):
		self.clearGhosts()
		if self.__canPlaceHere(self.__determineOccupyingCells(chartype, angle, gridx, gridy)) == 0:
			return 0
		self.party_members.append(CharacterSprite((0,0), angle, chartype, 0))
		self.party_positions.append((gridx, gridy))
		self.__updateGrid()
		self.__calculateRotationMaps()
		return 1

	# Creates a "ghost" image of a character at this location, for previewing purposes.
	# Only one such "ghost" character can be on the grid at any time.
	def previewCharacter(self, chartype, angle, gridx, gridy):
		self.clearGhosts()
		if self.__canPlaceHere(self.__determineOccupyingCells(chartype, angle, gridx, gridy)) == 0:
			return 0
		newchar = CharacterSprite((0,0), angle, chartype, 1)
		self.party_members.append(newchar)
		self.party_positions.append((gridx, gridy))
		self.__updateGrid()
		return 1

	#Gets the grid cells (with top-left at (gridx,gridy)) this given character would occupy at the given angle
	def __determineOccupyingCells(self, chartype, angle, gridx, gridy):
		if (chartype == SHIELD):
			return [(gridx,gridy),(gridx+1,gridy),(gridx,gridy+1),(gridx+1,gridy+1)]
		if (chartype == DOUBLE_SHOT):
			if angle == LEFT or angle == RIGHT:
				return[(gridx,gridy),(gridx+1,gridy)]
			else:
				return[(gridx,gridy),(gridx,gridy+1)]
		return [(gridx,gridy)]

	# Given an array of (gridx, gridy) tuples, returns if it would be valid for a character to be placed there.
	# Returns 1 if it is a valid placement, 0 otherwise.
	def __canPlaceHere(self, gridlist):
		for coord in gridlist:
			if self.getCharacter(coord[0],coord[1]) != -1:
				return 0
			for axis in coord:
				if axis < 0 or axis >= GRID_SIZE:
					return 0
		return 1

	# Remove all "ghost" characters from the grid
	def clearGhosts(self):
		updatedCharList = []
		updatedPosList = []
		for i in range(len(self.party_members)):
			if self.party_members[i].ghost != 1:
				updatedCharList.append(self.party_members[i])
				updatedPosList.append(self.party_positions[i])
		self.party_members = updatedCharList
		self.party_positions = updatedPosList

	def removeCharacter(self, gridx, gridy):
		updatedCharList = []
		updatedPosList = []
		removePos = (self.grid_contents[int(gridx)][int(gridy)][0], self.grid_contents[int(gridx)][int(gridy)][1])
		for i in range(len(self.party_members)):
			if self.party_positions[i] != removePos:
				updatedCharList.append(self.party_members[i])
				updatedPosList.append(self.party_positions[i])
		self.party_members = updatedCharList
		self.party_positions = updatedPosList
		self.__updateGrid()		
		self.__calculateRotationMaps()

	# Returns the number of characters currently placed into this grid.
	def numberOfCharacters(self):
		count = 0
		for member in self.party_members:
			if member.ghost == 0:
				count += 1
		return count

	# Returns the Character enum of the character occupying this cell of the grid,
	# or -1 if no character is in this cell.
	def getCharacter(self, gridx, gridy):
		if gridx < 0 or gridy < 0 or gridx >= GRID_SIZE or gridy >= GRID_SIZE:
			return -1
		return self.grid_contents[int(gridx)][int(gridy)][2]

	# Rotates the character at (gridx, gridy) counter-clockwise 90 degrees.
	# Returns 1 if the rotation was successful, 0 otherwise.
	def rotateCharacterAt(self, gridx, gridy):
		if self.getCharacter(gridx, gridy) == -1:
			return 0
		findPosition = (self.grid_contents[int(gridx)][int(gridy)][0], self.grid_contents[int(gridx)][int(gridy)][1])
		for i in range(len(self.party_positions)):
			if self.party_positions[i] == findPosition:
				if self.party_members[i].chartype == DOUBLE_SHOT:
					#The 1x2 character has some weird rotation handling
					newAngle = (self.party_members[i].rotation + 90) % 360
					remPos = self.party_positions[i]
					remAngle = self.party_members[i].rotation
					self.removeCharacter(gridx, gridy)
					if self.__canPlaceHere(self.__determineOccupyingCells(DOUBLE_SHOT, newAngle, remPos[0], remPos[1])) == 0:
						self.appendCharacter(DOUBLE_SHOT, remAngle, remPos[0], remPos[1])
						return 0
					else:
						self.appendCharacter(DOUBLE_SHOT, newAngle, remPos[0], remPos[1])
				else:
					self.party_members[i].rotateRelative(90)
				self.__updateGrid()
				return 1
		return 0

	# Rotates the entire party clockwise by 90 degrees
	def __rotatePartyCounterClockwise(self):
		for _ in range(3):
			self.__rotatePartyClockwise()

	# Rotates the entire party clockwise by 90 degrees
	def __rotatePartyClockwise(self):
		updatedPosList = []
		self.grid_angle = (self.grid_angle-90) % 360
		for i in range(len(self.party_members)):
			self.party_members[i].rotateRelative(-90)
			if self.party_members[i].chartype != DOUBLE_SHOT:
				if self.party_members[i].chartype == SHIELD:
					gridbound = GRID_SIZE-1
				else:
					gridbound = GRID_SIZE
				tempGrid = [[0 for _ in range(gridbound)] for _ in range(gridbound)]
				tempGrid[int(self.party_positions[i][0])][int(self.party_positions[i][1])] = 1
				ccwGrid = list(zip(*tempGrid))[::-1]
				for col in range(gridbound):
					for row in range(gridbound):
						if ccwGrid[col][row] == 1:
							updatedPosList.append((col,row))
							break
			else:
				#1x2 Character requires special rotation handling.
				if self.party_members[i].rotation == LEFT or self.party_members[i].rotation == RIGHT:
					updatedPosList.append((self.double_posmapUD[int(self.party_positions[i][1])][int(self.party_positions[i][0])][0]
										 ,self.double_posmapUD[int(self.party_positions[i][1])][int(self.party_positions[i][0])][1]))
				else:
					updatedPosList.append((self.double_posmapLR[int(self.party_positions[i][1])][int(self.party_positions[i][0])][0]
					 					 ,self.double_posmapLR[int(self.party_positions[i][1])][int(self.party_positions[i][0])][1]))

		self.party_positions = updatedPosList
		self.__updateGrid()

	#Store a copy of the party configuration in each of the four party orientations
	def __calculateRotationMaps(self):
		ind = 0
		self.rot_party_positions = []
		self.rot_party_directions = []
		self.rot_grid_contents = []
		for i in range(4):
			self.rot_party_positions.append([])
			self.rot_party_directions.append([])
			self.rot_grid_contents.append([])
		for i in range(4):
			self.__rotatePartyClockwise()
			if self.grid_angle == RIGHT:
				ind = 0
			elif self.grid_angle == UP:
				ind = 1
			elif self.grid_angle == LEFT:
				ind = 2
			else:
				ind = 3
			self.rot_party_positions[ind] = copy.deepcopy(self.party_positions)
			self.rot_grid_contents[ind] = copy.deepcopy(self.grid_contents)
			for char in self.party_members:
				self.rot_party_directions[ind].append(char.rotation) 

	# Rotate the entire party to the given direction
	# If visual = 0, skip updating the position where the party members will be drawn
	def setPartyRotation(self, direction, visual):
		ind = 0
		if direction == RIGHT:
			ind = 0
		elif direction == UP:
			ind = 1
		elif direction == LEFT:
			ind = 2
		else:
			ind = 3		
		self.grid_angle = direction
		self.party_positions = copy.deepcopy(self.rot_party_positions[ind])
		self.grid_contents = copy.deepcopy(self.rot_grid_contents[ind])
		if visual != 0:
			for i in range(len(self.party_members)):
				self.party_members[i].rotate(self.rot_party_directions[ind][i])
				self.party_members[i].rect.topleft = (self.grid_position[0]+self.party_positions[i][0]*CELL_SIZE,self.grid_position[1]+self.party_positions[i][1]*CELL_SIZE)
		else:
			for i in range(len(self.party_members)):
				self.party_members[i].rotation = self.rot_party_directions[ind][i]


	# Set the position on the screen where the grid should be drawn at
	def gridPosition(self, x, y):
		self.grid_position = (x,y)
		self.__updateGrid()

	# Syncs the contents of the grid_contents array based on the contents of the party_members/party_positions array.
	# Also updates the contents of party_members array based on the contents of the grid_position tuple.
	def __updateGrid(self):
		self.grid_contents = [[(0,0,-1) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)] # Start with a clean slate for the grid
		for i in range(len(self.party_members)):
			# For each party member, get the grid cells they occupy, and use this to update the grid_contents array
			populateCells = self.__determineOccupyingCells(self.party_members[i].chartype, self.party_members[i].rotation, self.party_positions[i][0], self.party_positions[i][1])	
			for cell in populateCells:
				if self.party_members[i].ghost == 0:
					ct = self.party_members[i].chartype
				else:
					ct = -1
				self.grid_contents[int(cell[0])][int(cell[1])] = (self.party_positions[i][0], self.party_positions[i][1], ct)
			# Update where on the screen this character will be drawn
			self.party_members[i].rect.topleft = (self.grid_position[0]+self.party_positions[i][0]*CELL_SIZE,self.grid_position[1]+self.party_positions[i][1]*CELL_SIZE)

	# Given a pixel coordinate within the game screen, return the cooresponding coordinate within the grid space
	# Returns (-1,-1) if outside the bounds of the grid
	def screenToGridCoords(self, sx, sy):
		if sx < self.grid_position[0] or sy < self.grid_position[1] or sx >= self.grid_position[0]+CELL_SIZE*GRID_SIZE or sy >= self.grid_position[1]+CELL_SIZE*GRID_SIZE:
			return (-1,-1)
		bx = sx - self.grid_position[0]
		by = sy - self.grid_position[1]
		return (math.floor(bx/CELL_SIZE), math.floor(by/CELL_SIZE))

	# Renders the grid on screen

	def renderGrid(self, screen):
		pygame.draw.rect(screen, self.grid_color, (self.grid_position[0], self.grid_position[1]
			                   , GRID_SIZE*CELL_SIZE, GRID_SIZE*CELL_SIZE), 3)
		for row in range(1,GRID_SIZE):
			pygame.draw.line(screen, self.grid_color, (self.grid_position[0], self.grid_position[1]+row*CELL_SIZE)
				                               , (self.grid_position[0]+GRID_SIZE*CELL_SIZE, self.grid_position[1]+row*CELL_SIZE), 1)
		for col in range(1,GRID_SIZE):
			pygame.draw.line(screen, self.grid_color, (self.grid_position[0]+col*CELL_SIZE, self.grid_position[1])
				                               , (self.grid_position[0]+col*CELL_SIZE, self.grid_position[1]+GRID_SIZE*CELL_SIZE), 1)
		if self.facing_indicator == 1:
			if self.grid_angle == RIGHT:
				pygame.draw.polygon(screen, self.grid_color, ((self.grid_position[0]+GRID_SIZE*CELL_SIZE,self.grid_position[1])
					,(self.grid_position[0]+GRID_SIZE*CELL_SIZE+GRID_ARROW_SIZE,self.grid_position[1]+(GRID_SIZE*CELL_SIZE)/2)
					,(self.grid_position[0]+GRID_SIZE*CELL_SIZE,self.grid_position[1]+GRID_SIZE*CELL_SIZE)), 0)
			elif self.grid_angle == UP:
				pygame.draw.polygon(screen, self.grid_color, ((self.grid_position[0],self.grid_position[1])
					,(self.grid_position[0]+(GRID_SIZE*CELL_SIZE)/2,self.grid_position[1]-GRID_ARROW_SIZE)
					,(self.grid_position[0]+GRID_SIZE*CELL_SIZE,self.grid_position[1])), 0)
			elif self.grid_angle == LEFT:
				pygame.draw.polygon(screen, self.grid_color, ((self.grid_position[0],self.grid_position[1])
					,(self.grid_position[0]-GRID_ARROW_SIZE,self.grid_position[1]+(GRID_SIZE*CELL_SIZE)/2)
					,(self.grid_position[0],self.grid_position[1]+GRID_SIZE*CELL_SIZE)), 0)
			elif self.grid_angle == DOWN:
				pygame.draw.polygon(screen, self.grid_color, ((self.grid_position[0],self.grid_position[1]+GRID_SIZE*CELL_SIZE)
					,(self.grid_position[0]+(GRID_SIZE*CELL_SIZE)/2,self.grid_position[1]+GRID_SIZE*CELL_SIZE+GRID_ARROW_SIZE)
					,(self.grid_position[0]+GRID_SIZE*CELL_SIZE,self.grid_position[1]+GRID_SIZE*CELL_SIZE)), 0)

		for member in self.party_members:
			pygame.sprite.RenderPlain(member).draw(screen)
	
	# resize the grid based on the side of the board
	def resizeGrid(self, width, height, margin):
		global CELL_SIZE
		CELL_SIZE = width + margin
		#self.facing_indicator = 0 # do not show the grid facing arrow
		for member in self.party_members:
			member.scale(width, height, margin)
	
	def maxHealth(self):
		# raking is hitting multiple squares of the same element. it hurts.
		# type 0 = 20 health
		# type 1 = 20 health, can be raked
		# type 2 = 80 health, can be raked
		self.health = 0
		for element in self.party_members:
			if element.chartype == 0:
				self.health += 20
			elif element.chartype == 1:
				self.health += 20
			elif element.chartype == 2:
				self.health += 80

	
