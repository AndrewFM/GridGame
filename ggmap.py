# Data structure for the playing grid that the game takes place on.
import pygame
import ggparty
import ggmove
from copy import deepcopy

global GGEVAL
GGEVAL = False

# Enums/Constants
#  -- Mouse Buttons
MOUSE_LEFT = 1
MOUSE_RIGHT = 3

class MapGrid():	
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
	BOARD_SIZE = 600
	CONSOLE_SIZE = 120
	GRID_SIZE = 15
	WIDTH = (int)(BOARD_SIZE*4/(5*GRID_SIZE+1))
	HEIGHT = (int)(BOARD_SIZE*4/(5*GRID_SIZE+1))
 
# This sets the margin between each cell
	MARGIN = BOARD_SIZE/(5*GRID_SIZE+1)

	def __init__(self, width, height):
		# This sets the WIDTH and HEIGHT of each grid location and the MARGIN between each cell
		self.WIDTH = width
		self.HEIGHT = height
		self.MARGIN = 5
		self.grid = []

		# Initialize command variables
		self.exe = 0
		
		# Initialize text variables
		if not GGEVAL:
			self.myfont = pygame.font.SysFont("arial bold",(int)(BOARD_SIZE/15))
			self.healthfont = pygame.font.SysFont("arial bold",(int)(BOARD_SIZE/30))
		
		for row in range(GRID_SIZE):
	# Add an empty array that will hold each cell
	# in this row
			self.grid.append([])
			for column in range(GRID_SIZE):
				self.grid[row].append(0)  # Append a cell
		# create a new party
		party = ggparty.PartyGrid()
		
		# Set the HEIGHT and WIDTH of the screen
		WINDOW_SIZE = [BOARD_SIZE, BOARD_SIZE+CONSOLE_SIZE]
		if not GGEVAL:
			screen = pygame.display.set_mode(WINDOW_SIZE)
 
	# Set title of screen
		if not GGEVAL:
			pygame.display.set_caption("Arena Combat Game")
			# Loop until the user clicks the close button.
			done = False
 
	# Used to manage how fast the screen updates
		if not GGEVAL:
			clock = pygame.time.Clock()
			delay = 0
 
	# Initialize text outputs
		if not GGEVAL:
			myfont = pygame.font.SysFont("arial bold",22)
			currentalert = []

	# Initialize command variables
		self.mstep = ggmove.Move()
		
# Set row 1, cell 5 to one. (Remember rows and
# column numbers start at zero.)
		self.grid = [[0 for row in range(10)] for column in range(10)]

	def update(self, event, screen, huPlayer, aiPlayers):
		#TODO: handling of keyboard input, mouse clicks, etc for the map scene.
		# Particuarly, inputting the movement sequences, and clicking the buttons to go to the simulation phase.
		if not GGEVAL:
			if event.type == pygame.QUIT:  # If user clicked close
				return 0  # Flag that we are done so we exit this loop
			elif event.type == pygame.KEYDOWN: # If user presses a key
				if event.key == pygame.K_BACKSPACE and huPlayer.cmd_id > 0: # If key is backspace, and any commands have been enterred
					huPlayer.cmd_id -= 1 # Decrement command ID
					huPlayer.cmd_seq[huPlayer.cmd_id] = -1 # Remove last entered command
				elif event.key == pygame.K_RETURN: # If key is return
					self.atklocs_seq = []
					currentalert = [] # Clear current alert
					self.exe = 1 # We're now in the execution phase
					for currentAI in aiPlayers:
						currentAI.cmd_seq = currentAI.ai_control.decideMoves(currentAI, aiPlayers + [huPlayer]) # get AI commands for each step
				elif huPlayer.cmd_id < 3:
					if event.key == pygame.K_UP: # Directional arrow keys
						huPlayer.cmd_seq[huPlayer.cmd_id] = ggparty.UP # Add corresponding command to the sequence
						huPlayer.cmd_id += 1 # Increment command ID (command 0, command 1, command 2)
						#player.loc[0][1] -= 1
					elif event.key == pygame.K_DOWN:
						huPlayer.cmd_seq[huPlayer.cmd_id] = ggparty.DOWN # Add corresponding command to the sequence
						huPlayer.cmd_id += 1 # Increment command ID (command 0, command 1, command 2)
						#player.loc[0][1] += 1
					elif event.key == pygame.K_RIGHT:
						huPlayer.cmd_seq[huPlayer.cmd_id] = ggparty.RIGHT # Add corresponding command to the sequence
						huPlayer.cmd_id += 1 # Increment command ID (command 0, command 1, command 2)
						#player.loc[0][0] += 1
					elif event.key == pygame.K_LEFT:
						huPlayer.cmd_seq[huPlayer.cmd_id] = ggparty.LEFT # Add corresponding command to the sequence
						huPlayer.cmd_id += 1 # Increment command ID (command 0, command 1, command 2)
						#player.loc[0][0] -= 1
		else:
			for currentAI in aiPlayers:
						currentAI.cmd_seq = currentAI.ai_control.decideMoves(currentAI, aiPlayers + [huPlayer]) # get AI commands for each step
		return 1
	
	def executeStep(self, screen, huPlayer, aiPlayers, step):
		atklocs = []
		
		# For human player
		if huPlayer is not None:
			self.mstep.oneStep(huPlayer,huPlayer.cmd_seq[step])
			if not GGEVAL:
				self.drawParty(screen, huPlayer)
		
		# For AI players
		for currentAI in aiPlayers:
			if currentAI.health > 0:
				self.mstep.oneStep(currentAI,currentAI.cmd_seq[step])
				self.drawParty(screen, currentAI)
				self.mstep.attack(currentAI, huPlayer, aiPlayers, screen)
		self.mstep.attack(huPlayer, huPlayer, aiPlayers, screen)
		
		if not GGEVAL:
			pygame.display.flip()	
			pygame.time.wait(500) # Wait between showing each step. Time is in milliseconds.

		# Record current health totals and add them to the record for each player
		if huPlayer is not None:
			huPlayer.healthRecord.append(huPlayer.health)
		for currentAI in aiPlayers:
			currentAI.healthRecord.append(currentAI.health)		
	
	#party: ggparty.PartyGrid() object
	def addPartyToMap(self, party, angle, gridx, gridy):
		party.resizeGrid(WIDTH,HEIGHT,MARGIN)
		party.supergrid_location = [gridx, gridy]
		#self.grid[gridx,gridy] = party
		#TODO: add a party onto the map grid at the given position
		todo = 0
	
	def drawParty(self, screen, party):
		if GGEVAL:
			return
		column = party.supergrid_location[1]
		row = party.supergrid_location[0]
		party.gridPosition((MARGIN + WIDTH) * column + MARGIN,
							(MARGIN + HEIGHT) * row + MARGIN)
		party.renderGrid(screen)
		label = self.myfont.render(str(party.health),1,RED)
		screen.blit(label,((MARGIN + WIDTH) * column + MARGIN,
							(MARGIN + HEIGHT) * row + MARGIN))

	# Renders the map on screen
	def renderGrid(self, screen):
		# Set the screen background
		screen.fill(BLACK)
	    # Draw the grid
		for row in range(GRID_SIZE):
			for column in range(GRID_SIZE):
				color = WHITE
				pygame.draw.rect(screen,
								color,
								[(MARGIN + WIDTH) * column + MARGIN,
								(MARGIN + HEIGHT) * row + MARGIN,
								WIDTH,
								HEIGHT])
	
	# Renders the console on the screen
	def renderConsole(self, screen, huPlayer, currentalert):
		if GGEVAL:
			return
		# Draw the input console
		color = WHITE
		pygame.draw.rect(screen,
						color,
						[MARGIN,
						BOARD_SIZE,
						BOARD_SIZE - 2*MARGIN,
						CONSOLE_SIZE - MARGIN])
		
		# Write the command sequence in the input console
		offset = 0
		for command in huPlayer.cmd_seq:
			txt = "[empty]"
			if command == ggparty.UP:
				txt = "UP"
			elif command == ggparty.DOWN:
				txt = "DOWN"
			elif command == ggparty.LEFT:
				txt = "LEFT"
			elif command == ggparty.RIGHT:
				txt = "RIGHT"
			label = self.myfont.render(txt,1,BLACK)
			screen.blit(label, (MARGIN, BOARD_SIZE+offset))
			offset += BOARD_SIZE/20
		# Write current alert into input console
		if currentalert != []:
			label = self.myfont.render(currentalert,1,RED)
			screen.blit(label, (BOARD_SIZE/2+MARGIN, BOARD_SIZE))