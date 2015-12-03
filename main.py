# The main file which should be run in order to launch the game.
from pygame.locals import *
import pygame
import ggcreateparty
import ggmap
import ggparty
import ggai

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
			aiPlayers = []
			for i in range(NUM_AI_PLAYERS):
				aiPlayers.append(ggai.constructParty())
				aiPlayers[i].assignAI(ggai.AIOpponent())
			# huParty.party_members[x].chartype gives element type
			# '' .rotation gives element angle
			# huParty.party_position[x]
			# CharacterSprite class in ggparty has this info
			if huPlayer != -1:
				switchToScene(GAME_GRID)
				mapScene.addPartyToMap(huPlayer,ggparty.UP,starts[0][0],starts[0][1])
				huPlayer.grid_color = ggparty.BLUE
				huPlayer.maxHealth()
				for i in range(NUM_AI_PLAYERS):
					mapScene.addPartyToMap(aiPlayers[i],ggparty.UP,starts[i+1][0],starts[i+1][1])
					aiPlayers[i].grid_color = ggparty.RED
					aiPlayers[i].maxHealth()
		

		
		
		# [SCENE] Actual Game
		elif current_scene == GAME_GRID:
			running = mapScene.update(event, screen, huPlayer, aiPlayers)
			
			# Check victory and defeat conditions
			if huPlayer.alive == 0:
				currentalert = 'Game over'
				delay = 3000
				running = 0
			elif len([x for x in aiPlayers if x.alive == 1]) == 0:
				currentalert = 'You win!'
				delay = 3000
				running = 0
			
			
			mapScene.renderGrid(screen)
			mapScene.renderConsole(screen, huPlayer, currentalert)
			if mapScene.exe == 0:
				mapScene.drawParty(screen, huPlayer)
				for currentAI in aiPlayers:
					mapScene.drawParty(screen, currentAI)
			else: # execute step
				mapScene.executeStep(screen, huPlayer, aiPlayers, step)
				step += 1
			
			if step >= 3: # If we've done all 3 steps, end the execution phase
				step = 0
				mapScene.exe = 0
				huPlayer.cmd_seq = ["[empty]","[empty]","[empty]"]
				huPlayer.cmd_id = 0
		
			if huPlayer.health <= 0:
				huPlayer.alive = 0
			for currentAI in aiPlayers:
				if currentAI.health <= 0:
					currentAI.alive = 0
					currentAI.supergrid_location = [-10,-10]
			

		pygame.display.flip()
		pygame.time.wait(delay)

pygame.quit()