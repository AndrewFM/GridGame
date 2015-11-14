import pygame
import ggmove
import ggai
from copy import deepcopy

def drawPlayers(status, ploc, facing, health, hu_img, ai_img): # draw player graphics
	import pygame
	for i in range(NUM_PLAYERS):
		if status[i] == 1:
			img = hu_img
		else:
			img = ai_img
		rotimg = pygame.transform.rotate(img,facing[i])
		screen.blit(rotimg,((MARGIN + WIDTH) * ploc[i][0] + MARGIN,
						(MARGIN + HEIGHT) * ploc[i][1] + MARGIN))
		label = myfont.render(str(health[i]),1,BLACK)
		screen.blit(label,((MARGIN + WIDTH) * ploc[i][0] + MARGIN,
						(MARGIN + HEIGHT) * ploc[i][1] + MARGIN))

def drawAttacks(atklocs, img): # draw attack graphics
	# each attack in atklocs is in [attacker location, defender location] format
	if atklocs != []:
		import pygame
		color = RED
		for loc in atklocs:
			# draw beam between attacker and defender
			pygame.draw.rect(screen,
							color,
							[(MARGIN + WIDTH) * loc[0][0] + MARGIN + WIDTH/2,
							(MARGIN + HEIGHT) * loc[0][1] + MARGIN + HEIGHT/2,
							(MARGIN + WIDTH) * (loc[1][0] - loc[0][0]),
							(MARGIN + HEIGHT) * (loc[1][1] - loc[0][1])])
			# draw explosion on defender
			screen.blit(img,((MARGIN + WIDTH) * loc[1][0] + MARGIN,
						(MARGIN + HEIGHT) * loc[1][1] + MARGIN))
			

def alert(message):
	if message != []:
		label = myfont.render(message,1,RED)
		screen.blit(label, (BOARD_SIZE/2+MARGIN, BOARD_SIZE))

# Declare globals

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

# Define some colors
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

# Declare player object 
class player:
	loc = []
	loc_intermediate = []
	status = [] # 1 = human, 0 = computer, -1 = dead
	starts = [[1,1],
		[GRID_SIZE-2,GRID_SIZE-2],
		[GRID_SIZE-2,1],
		[1,GRID_SIZE-2]]
	facing = []
	facing_intermediate = []
	health = []
	health_intermediate = []
 
# Create a 2 dimensional array. A two dimensional
# array is simply a list of lists.
#grid = []
#for row in range(GRID_SIZE):
    # Add an empty array that will hold each cell
    # in this row
#    grid.append([])
#    for column in range(GRID_SIZE):
#        grid[row].append(0)  # Append a cell

# Initialize player start locations and status
NUM_PLAYERS = 3 # 1-4
#player.loc = []
#player.status = [] # 1 = human, 0 = computer, -1 = dead
#player.starts = [[1,1],
#			[GRID_SIZE-2,GRID_SIZE-2],
#			[GRID_SIZE-2,1],
#			[1,GRID_SIZE-2]]
for i in range(NUM_PLAYERS):
	player.loc += [player.starts[i]]
	player.facing += [90.0]
	player.health += [100]
	if i == 0:
		player.status += [1]
	else:
		player.status += [0]	

# Initialize pygame
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
myfont = pygame.font.SysFont("arial bold",BOARD_SIZE/15)
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

# -------- Main Program Loop -----------
while not done:

	# Check victory and defeat conditions
	if max(player.status) < 1:
		currentalert = 'Game over'
		delay = 3000
		done = True
	elif len([x for x in player.status if x >= 0]) == 1:
		currentalert = 'You win!'
		delay = 3000
		done = True

	for event in pygame.event.get():  # User did something
		if event.type == pygame.QUIT:  # If user clicked close
			done = True  # Flag that we are done so we exit this loop
		elif event.type == pygame.KEYDOWN: # If user presses a key
			if event.key == pygame.K_BACKSPACE and cmd_id > 0: # If key is backspace, and any commands have been enterred
				cmd_id -= 1 # Decrement command ID
				cmd_seq[cmd_id] = "[empty]" # Remove last entered command
			elif event.key == pygame.K_RETURN: # If key is return
				currentalert = [] # Clear current alert
				exe = 1 # We're now in the execution phase
				AI = ggai.AIOpponent()
				AIcmds = []
				player.loc_intermediate = []
				player.facing_intermediate = []
				player.health_intermediate = []
				atklocs_seq = []
				for AIplayer in range(NUM_PLAYERS-1): # Get moves from each AI player. Currently assumes only player 1 is human.
					AIcmds += [AI.decideMoves('this doesnt matter yet')]
				for step in range(3): # Execute each step
					cmds = [cmd_seq[step]] # Player command for each step
					for AIplayer in range(NUM_PLAYERS-1):
						cmds += [AIcmds[AIplayer][step]] # AI commands for each step
					mstep = ggmove.Move()
					player.loc, player.facing = mstep.oneStep(player.loc,player.facing,player.status,cmds,GRID_SIZE) # Execute current step
					player.health, atklocs = mstep.attack(player.loc,player.facing,player.health) #Execute attacks after each move
					# Check to see if players are dead
					for i in range(NUM_PLAYERS):
						if player.health[i] <= 0:
							player.status[i] = -1
							player.loc[i] = [-10-i,-10-i] # Out of sight, out of mind
							player.health[i] = 1 # Don't reset them as dead at each step
							currentalert = 'player ' + str(i+1) + ' dead'
					player.loc_intermediate.append(deepcopy(player.loc)) # Record position at each step so we can display it
					player.facing_intermediate.append(deepcopy(player.facing)) # Record facing at each step
					player.health_intermediate.append(deepcopy(player.health)) # Record health after each move
					atklocs_seq.append(deepcopy(atklocs))
				cmd_seq = ["[empty]","[empty]","[empty]"]
				cmd_id = 0
			elif cmd_id < 3:
				if event.key == pygame.K_UP: # Directional arrow keys
					cmd_seq[cmd_id] = "UP" # Add corresponding command to the sequence
					cmd_id += 1 # Increment command ID (command 0, command 1, command 2)
					#player.loc[0][1] -= 1
				elif event.key == pygame.K_DOWN:
					cmd_seq[cmd_id] = "DOWN" # Add corresponding command to the sequence
					cmd_id += 1 # Increment command ID (command 0, command 1, command 2)
					#player.loc[0][1] += 1
				elif event.key == pygame.K_RIGHT:
					cmd_seq[cmd_id] = "RIGHT" # Add corresponding command to the sequence
					cmd_id += 1 # Increment command ID (command 0, command 1, command 2)
					#player.loc[0][0] += 1
				elif event.key == pygame.K_LEFT:
					cmd_seq[cmd_id] = "LEFT" # Add corresponding command to the sequence
					cmd_id += 1 # Increment command ID (command 0, command 1, command 2)
					#player.loc[0][0] -= 1
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
		offset += BOARD_SIZE/20
	# Write current alert into input console
	alert(currentalert)
	
	if exe == 1: # If in execution phase, draw players at each step
		drawPlayers(player.status,player.loc_intermediate[showstep],player.facing_intermediate[showstep],player.health_intermediate[showstep],hu_img,ai_img)
		drawAttacks(atklocs_seq[showstep], explosion)
		pygame.time.wait(500) # Wait between showing each step. Time is in milliseconds.
		showstep += 1
	
	else:	# If not in the execution phase, just draw the players in the grid normally
		drawPlayers(player.status,player.loc,player.facing,player.health,hu_img,ai_img)
	
	if showstep >= 3: # If we've done all 3 steps, end the execution phase
		exe = 0
		showstep = 0
	
	# Limit to 60 frames per second
	clock.tick(60)
 
    # Go ahead and update the screen with what we've drawn.
	pygame.display.flip()
	pygame.time.wait(delay) # Wait if told to do so

# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
pygame.quit()
