import pygame
import math

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
GRID_COLOR = (0,0,0)
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

	def rotate(self, angle):
		self.rotation = angle
		self.image = pygame.transform.rotate(self.src_image, angle)

	#Increment the current rotation by some amount
	def rotateRelative(self, angle):
		newdegrees = (self.rotation + angle) % 360
		self.rotate(newdegrees)


# Data Structure for 3x3 Character Parties
class PartyGrid():

	def __init__(self):
		self.grid_position = (0,0)
		self.grid_angle = RIGHT	   # Facing direction of the entire party grid as a whole
		self.party_members = []    # Contains CharacterSprite elements. Must be in parallel with array below.
		self.party_positions = []  # Contains (gridx, gridy) elements. Must be in parallel with array above.
		self.grid_contents = [[(0,0,-1) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)] # Contains Character enum elements & grid pos of source character.		

	# Returns 1 if the character was successfully inserted, 0 otherwise.
	# Angles should be in degrees, should be between 0 and 2pi, and should always be multiples of pi/2.
	def appendCharacter(self, chartype, angle, gridx, gridy):
		self.clearGhosts()
		if self.__canPlaceHere(self.__determineOccupyingCells(chartype, angle, gridx, gridy)) == 0:
			return 0
		self.party_members.append(CharacterSprite((0,0), angle, chartype, 0))
		self.party_positions.append((gridx, gridy))
		self.__updateGrid()
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
			if angle == 0 or angle == 180 or angle == 360:
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
		removePos = (self.grid_contents[gridx][gridy][0], self.grid_contents[gridx][gridy][1])
		for i in range(len(self.party_members)):
			if self.party_positions[i] != removePos:
				updatedCharList.append(self.party_members[i])
				updatedPosList.append(self.party_positions[i])
		self.party_members = updatedCharList
		self.party_positions = updatedPosList
		self.__updateGrid()		

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
		return self.grid_contents[gridx][gridy][2]

	# Rotates the character at (gridx, gridy) counter-clockwise 90 degrees.
	# Returns 1 if the rotation was successful, 0 otherwise.
	def rotateCharacterAt(self, gridx, gridy):
		if self.getCharacter(gridx, gridy) == -1:
			return 0
		findPosition = (self.grid_contents[gridx][gridy][0], self.grid_contents[gridx][gridy][1])
		for i in range(len(self.party_positions)):
			if self.party_positions[i] == findPosition:
				self.party_members[i].rotateRelative(90)
				self.__updateGrid()
				return 1
		return 0

	# Rotates the entire party clockwise by 90 degrees
	def rotatePartyCounterClockwise(self):
		for _ in range(3):
			self.rotatePartyClockwise()

	# Rotates the entire party clockwise by 90 degrees
	def rotatePartyClockwise(self):
		updatedPosList = []
		self.grid_angle = (self.grid_angle-90) % 360
		for i in range(len(self.party_members)):
			self.party_members[i].rotateRelative(-90)
			tempGrid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
			tempGrid[self.party_positions[i][0]][self.party_positions[i][1]] = 1
			ccwGrid = list(zip(*tempGrid))[::-1]
			for col in range(GRID_SIZE):
				for row in range(GRID_SIZE):
					if ccwGrid[col][row] == 1:
						updatedPosList.append((col,row))
						break

		self.party_positions = updatedPosList
		self.__updateGrid()

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
				self.grid_contents[cell[0]][cell[1]] = (self.party_positions[i][0], self.party_positions[i][1], ct)
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
		pygame.draw.rect(screen, GRID_COLOR, (self.grid_position[0], self.grid_position[1]
			                   , GRID_SIZE*CELL_SIZE, GRID_SIZE*CELL_SIZE), 3)
		for row in range(1,GRID_SIZE):
			pygame.draw.line(screen, GRID_COLOR, (self.grid_position[0], self.grid_position[1]+row*CELL_SIZE)
				                               , (self.grid_position[0]+GRID_SIZE*CELL_SIZE, self.grid_position[1]+row*CELL_SIZE), 1)
		for col in range(1,GRID_SIZE):
			pygame.draw.line(screen, GRID_COLOR, (self.grid_position[0]+col*CELL_SIZE, self.grid_position[1])
				                               , (self.grid_position[0]+col*CELL_SIZE, self.grid_position[1]+GRID_SIZE*CELL_SIZE), 1)

		if self.grid_angle == RIGHT:
			pygame.draw.polygon(screen, GRID_COLOR, ((self.grid_position[0]+GRID_SIZE*CELL_SIZE,self.grid_position[1])
				,(self.grid_position[0]+GRID_SIZE*CELL_SIZE+GRID_ARROW_SIZE,self.grid_position[1]+(GRID_SIZE*CELL_SIZE)/2)
				,(self.grid_position[0]+GRID_SIZE*CELL_SIZE,self.grid_position[1]+GRID_SIZE*CELL_SIZE)), 0)
		elif self.grid_angle == UP:
			pygame.draw.polygon(screen, GRID_COLOR, ((self.grid_position[0],self.grid_position[1])
				,(self.grid_position[0]+(GRID_SIZE*CELL_SIZE)/2,self.grid_position[1]-GRID_ARROW_SIZE)
				,(self.grid_position[0]+GRID_SIZE*CELL_SIZE,self.grid_position[1])), 0)
		elif self.grid_angle == LEFT:
			pygame.draw.polygon(screen, GRID_COLOR, ((self.grid_position[0],self.grid_position[1])
				,(self.grid_position[0]-GRID_ARROW_SIZE,self.grid_position[1]+(GRID_SIZE*CELL_SIZE)/2)
				,(self.grid_position[0],self.grid_position[1]+GRID_SIZE*CELL_SIZE)), 0)
		elif self.grid_angle == DOWN:
			pygame.draw.polygon(screen, GRID_COLOR, ((self.grid_position[0],self.grid_position[1]+GRID_SIZE*CELL_SIZE)
				,(self.grid_position[0]+(GRID_SIZE*CELL_SIZE)/2,self.grid_position[1]+GRID_SIZE*CELL_SIZE+GRID_ARROW_SIZE)
				,(self.grid_position[0]+GRID_SIZE*CELL_SIZE,self.grid_position[1]+GRID_SIZE*CELL_SIZE)), 0)

		for member in self.party_members:
			pygame.sprite.RenderPlain(member).draw(screen)