# The main file which should be run in order to launch the game.
from pygame.locals import *
import pygame
import ggcreateparty
import ggmap
import ggparty
import ggai
import ggutils

# Enums/Constants
#  -- Scenes
CREATE_PARTY = 1
GAME_GRID = 2

# Import resources
img_char = [0 for x in range(3)]
img_char[0] = pygame.image.load("img/char_0.png")
img_char[1] = pygame.image.load("img/char_1.png")
img_char[2] = pygame.image.load("img/char_2.png")

# Game Initialization
pygame.init()
screen = pygame.display.set_mode((800,600), DOUBLEBUF)
clock = pygame.time.Clock()
fps = 60
running = 1
current_scene = CREATE_PARTY
partyScene = -1
mapScene = -1
NUM_AI_PLAYERS = 2
starts = [[0,0],
		[ggmap.GRID_SIZE-3,ggmap.GRID_SIZE-3],
		[ggmap.GRID_SIZE-3,0],
		[0,ggmap.GRID_SIZE-3]]
delay = 0
step = 0
		
# Initialize text outputs
currentalert = []

def switchToScene(sc):
	global current_scene, partyScene, mapScene
	current_scene = sc
	if sc == CREATE_PARTY:
		partyScene = ggcreateparty.CreateParty()
	elif sc == GAME_GRID:
		mapScene = ggmap.MapGrid(12,12)

switchToScene(current_scene)

# Game Loop
while running:
	
	dt = clock.tick(fps)
	event = pygame.event.poll()
	
	if event.type == pygame.QUIT:
		running = 0
	else:
		screen.fill((227,237,216))

		# [SCENE] Create Party
		if current_scene == CREATE_PARTY:
			partyScene.update(event)
			partyScene.render(screen)	

			huPlayer = partyScene.isFinished()
			gamePlayers = []

			# huParty.party_members[x].chartype gives element type
			# '' .rotation gives element angle
			# huParty.party_position[x]
			# CharacterSprite class in ggparty has this info
			if huPlayer != -1:
				gamePlayers.append(huPlayer)
				# Generate the contents of the AI agents' parties, and assign them an AI controller.
				for i in range(NUM_AI_PLAYERS):
					party = ggai.constructParty()
					party.assignAI(ggai.AIOpponent(i+1))
					gamePlayers.append(party)
				
				switchToScene(GAME_GRID)
				for i in range(len(gamePlayers)):
					mapScene.addPartyToMap(gamePlayers[i],ggparty.UP,starts[i][0],starts[i][1])
					if gamePlayers[i].isAI() == 0:
						gamePlayers[i].grid_color = ggparty.BLUE
					else:
						gamePlayers[i].grid_color = ggparty.RED
					gamePlayers[i].maxHealth()
		

		
		
		# [SCENE] Actual Game
		elif current_scene == GAME_GRID:
			running = mapScene.update(event, screen, gamePlayers)
			
			# Check victory and defeat conditions
			if len([x for x in gamePlayers if x.alive == 1 and x.isAI() == 0]) == 0:
				currentalert = 'Game over'
				delay = 3000
				running = 0
			elif len([x for x in gamePlayers if x.alive == 1 and x.isAI() == 1]) == 0:
				currentalert = 'You win!'
				delay = 3000
				running = 0
			
			
			huPlayer = ggutils.getHumanPlayer(gamePlayers)
			mapScene.renderGrid(screen)
			mapScene.renderConsole(screen, huPlayer, currentalert)
			if mapScene.exe == 0:
				for party in gamePlayers:
					mapScene.drawParty(screen, party)
			else: # execute step
				mapScene.executeStep(screen, gamePlayers, step)
				step += 1
			
			if step >= 3: # If we've done all 3 steps, end the execution phase
				step = 0
				mapScene.exe = 0
				huPlayer.cmd_seq = ["[empty]","[empty]","[empty]"]
				huPlayer.cmd_id = 0
		
			for party in gamePlayers:
				if party.health <= 0:
					party.alive = 0
					if party.isAI() == 1:
						party.supergrid_location = [-10,-10]
			

		pygame.display.flip()
		pygame.time.wait(delay)

pygame.quit()