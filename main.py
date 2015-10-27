# The main file which should be run in order to launch the game.
from pygame.locals import *
import pygame
import ggcreateparty
import ggmap

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

			if partyScene.isFinished() != -1:
				switchToScene(GAME_GRID)		

		# [SCENE] Actual Game
		elif current_scene == GAME_GRID:
			mapScene.update(event)
			mapScene.renderGrid(screen)

		pygame.display.flip()

pygame.quit()