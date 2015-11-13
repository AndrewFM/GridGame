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
	
	global BLACK
	global WHITE
	global GREEN
	global RED
	global BOARD_SIZE
	global CONSOLE_SIZE
	global WIDTH
	global HEIGHT
	global MARGIN
	global GRID_SIZE
	global NUM_PLAYERS
	global WINDOW_SIZE
	BLACK = (0, 0, 0)
	WHITE = (255, 255, 255)
	GREEN = (0, 255, 0)
	RED = (255, 0, 0)
 
# This sets the WIDTH and HEIGHT of each grid location, as well as the size of the grid
	BOARD_SIZE = 500;
	CONSOLE_SIZE = 100;
	GRID_SIZE = 10
	WIDTH = BOARD_SIZE*4/(5*GRID_SIZE+1)
	HEIGHT = BOARD_SIZE*4/(5*GRID_SIZE+1)
 
# This sets the margin between each cell
	MARGIN = BOARD_SIZE/(5*GRID_SIZE+1)

	def __init__(self, width, height):
		# This sets the WIDTH and HEIGHT of each grid location and the MARGIN between each cell
		self.WIDTH = width
		self.HEIGHT = height
		self.MARGIN = 5
		self.grid = []
		for row in range(GRID_SIZE):
			# Add an empty array that will hold each cell
			# in this row
			self.grid.append([])
			for column in range(GRID_SIZE):
				self.grid[row].append(0)  # Append a cell

# Set row 1, cell 5 to one. (Remember rows and
# column numbers start at zero.)
		#self.grid[1][5] = 1
		#self.grid = [[0 for row in range(10)] for column in range(10)]

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
		pygame.init()
 
# Set the HEIGHT and WIDTH of the screen
		WINDOW_SIZE = [BOARD_SIZE, BOARD_SIZE+CONSOLE_SIZE]
		screen = pygame.display.set_mode(WINDOW_SIZE)
 
# Set title of screen
		pygame.display.set_caption("Arena Combat Game")
		# Loop until the user clicks the close button.
		done = False
 
# Used to manage how fast the screen updates
		clock = pygame.time.Clock()
		delay = 0;
 
# Initialize text outputs
		myfont = pygame.font.SysFont("arial bold",22)
		currentalert = []

# Initialize command variables
		cmd_seq = ["[empty]","[empty]","[empty]"]
		cmd_id = 0
		exe = 0
		showstep = 0

# Initialize graphics
		hu_img = pygame.image.load('hu_player.png')
		hu_img = pygame.transform.scale(hu_img, (WIDTH, HEIGHT))
		ai_img = pygame.image.load('ai_player.png')
		ai_img = pygame.transform.scale(ai_img, (WIDTH, HEIGHT))
		explosion = pygame.image.load('explosion.jpg')
		explosion = pygame.transform.scale(explosion, (WIDTH, HEIGHT))
