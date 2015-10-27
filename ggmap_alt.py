import pygame
import ggmove
import ggai
from copy import deepcopy

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
 
# This sets the WIDTH and HEIGHT of each grid location
BOARD_SIZE = 255;
CONSOLE_SIZE = 100;
WIDTH = BOARD_SIZE*4/51
HEIGHT = BOARD_SIZE*4/51
 
# This sets the margin between each cell
MARGIN = BOARD_SIZE/51
 
# Create a 2 dimensional array. A two dimensional
# array is simply a list of lists.
GRID_SIZE = 10
grid = []
for row in range(GRID_SIZE):
    # Add an empty array that will hold each cell
    # in this row
    grid.append([])
    for column in range(GRID_SIZE):
        grid[row].append(0)  # Append a cell
 
# Set row 1, cell 5 to one. (Remember rows and
# column numbers start at zero.)
grid[1][5] = 1

# Initialize player start locations
NUM_PLAYERS = 2
ploc = []
pstarts = [[1,1],
			[GRID_SIZE-2,GRID_SIZE-2],
			[GRID_SIZE-2,1],
			[1,GRID_SIZE-2]]
for i in range(NUM_PLAYERS):
	ploc += [pstarts[i]]
 
# Initialize pygame
pygame.init()
 
# Set the HEIGHT and WIDTH of the screen
WINDOW_SIZE = [BOARD_SIZE, BOARD_SIZE+CONSOLE_SIZE]
screen = pygame.display.set_mode(WINDOW_SIZE)
 
# Set title of screen
pygame.display.set_caption("Array Backed Grid")
 
# Loop until the user clicks the close button.
done = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
 
# Initialize text outputs
myfont = pygame.font.SysFont("arial",15)

# Initialize command variables
cmd_seq = ["[empty]","[empty]","[empty]"]
cmd_id = 0
exe = 0
showstep = 0

# -------- Main Program Loop -----------
while not done:

	for event in pygame.event.get():  # User did something
		if event.type == pygame.QUIT:  # If user clicked close
			done = True  # Flag that we are done so we exit this loop
		elif event.type == pygame.KEYDOWN: # If user presses a key
			if event.key == pygame.K_BACKSPACE and cmd_id > 0: # If key is backspace, and any commands have been enterred
				cmd_id -= 1 # Decrement command ID
				cmd_seq[cmd_id] = "[empty]" # Remove last entered command
			elif event.key == pygame.K_RETURN: # If key is return
				exe = 1 # We're now in the executuon phase
				AI = ggai.AIOpponent()
				AIcmds = []
				ploc_intermediate = []
				for AIplayer in range(NUM_PLAYERS-1): # Get moves from each AI player. Currently assumes only player 1 is human.
					AIcmds += [AI.decideMoves('this doesnt matter yet')]
				for step in range(3): # Execute each step
					cmds = [cmd_seq[step]] # Player command for each step
					for AIplayer in range(NUM_PLAYERS-1):
						cmds += [AIcmds[AIplayer][step]] # AI commands for each step
					mstep = ggmove.Move()
					ploc = mstep.oneStep(ploc,cmds,GRID_SIZE) # Execute current step
					ploc_intermediate.append(deepcopy(ploc)) # Record each step so we can display it
					# *************************************** FIRING GOES HERE *********************************************************
				cmd_seq = ["[empty]","[empty]","[empty]"]
				cmd_id = 0
			elif cmd_id < 3:
				if event.key == pygame.K_UP: # Directional arrow keys
					cmd_seq[cmd_id] = "UP" # Add corresponding command to the sequence
					cmd_id += 1 # Increment command ID (command 0, command 1, command 2)
					#ploc[0][1] -= 1
				elif event.key == pygame.K_DOWN:
					cmd_seq[cmd_id] = "DOWN" # Add corresponding command to the sequence
					cmd_id += 1 # Increment command ID (command 0, command 1, command 2)
					#ploc[0][1] += 1
				elif event.key == pygame.K_RIGHT:
					cmd_seq[cmd_id] = "RIGHT" # Add corresponding command to the sequence
					cmd_id += 1 # Increment command ID (command 0, command 1, command 2)
					#ploc[0][0] += 1
				elif event.key == pygame.K_LEFT:
					cmd_seq[cmd_id] = "LEFT" # Add corresponding command to the sequence
					cmd_id += 1 # Increment command ID (command 0, command 1, command 2)
					#ploc[0][0] -= 1
        #elif event.type == pygame.MOUSEBUTTONDOWN:
            ## User clicks the mouse. Get the position
            #pos = pygame.mouse.get_pos()
            ## Change the x/y screen coordinates to grid coordinates
            #column = pos[0] // (WIDTH + MARGIN)
            #row = pos[1] // (HEIGHT + MARGIN)
            ## Set that location to zero
            #grid[row][column] = 1
            #print("Click ", pos, "Grid coordinates: ", row, column)

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
	for command in cmd_seq:
		label = myfont.render(command,1,BLACK)
		screen.blit(label, (MARGIN, BOARD_SIZE+offset))
		offset += 15
	
	# *********************** NEED FACING HERE *********************
	if exe == 1: # If in execution phase, draw players at each step
		color = GREEN
		for i in range(NUM_PLAYERS):
			pygame.draw.rect(screen,
							color,
							[(MARGIN + WIDTH) * ploc_intermediate[showstep][i][0] + MARGIN,
							(MARGIN + HEIGHT) * ploc_intermediate[showstep][i][1] + MARGIN,
							WIDTH,
							HEIGHT])
		pygame.time.wait(500) # Wait between showing each step. Time is in milliseconds.
		showstep += 1
	
	else:	# If not in the execution phase, just draw the players in the grid normally
		color = GREEN
		for i in range(NUM_PLAYERS):
			pygame.draw.rect(screen,
							color,
							[(MARGIN + WIDTH) * ploc[i][0] + MARGIN,
							(MARGIN + HEIGHT) * ploc[i][1] + MARGIN,
							WIDTH,
							HEIGHT])
	
	if showstep >= 3: # If we've done all 3 steps, end the execution phase
		exe = 0
		showstep = 0
	
	# Limit to 60 frames per second
	clock.tick(60)
 
    # Go ahead and update the screen with what we've drawn.
	pygame.display.flip()
 
# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
pygame.quit()
