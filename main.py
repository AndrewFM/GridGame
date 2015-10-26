# The main file which should be run in order to launch the game.
from pygame.locals import *
import pygame
import math
import ggparty
import ggmap

# Enum constants
#  -- Scenes
CREATE_PARTY = 1
GAME_GRID = 2
#  -- Mouse Buttons
LEFT = 1
RIGHT = 3

# Import resources
img_char = [0 for x in range(3)]
img_char[0] = pygame.image.load("img/char_0.png")
img_char[1] = pygame.image.load("img/char_1.png")
img_char[2] = pygame.image.load("img/char_2.png")

# Game Initialization
screen = pygame.display.set_mode((800,600), DOUBLEBUF)
clock = pygame.time.Clock()
fps = 60
running = 1
current_scene = CREATE_PARTY
partyCanvas = 0
mapCanvas = 0
selectedChar = 0
#pygame.mouse.getPos

def switchToScene(sc):
	global current_scene, partyCanvas, selectedChar, mapCanvas
	current_scene = sc
	if sc == CREATE_PARTY:
		partyCanvas = ggparty.PartyGrid()
		partyCanvas.gridPosition(25,25)
		selectedChar = ggparty.SINGLE_SHOT
	elif sc == GAME_GRID:
		mapCanvas = ggmap.MapGrid(12,12)

switchToScene(GAME_GRID)

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
			if event.type == pygame.MOUSEBUTTONDOWN:
				# Get the grid cell that we clicked on
				gridCoords = partyCanvas.screenToGridCoords(event.pos[0], event.pos[1])

				if event.button == LEFT and gridCoords != (-1,-1):
					if partyCanvas.getCharacter(gridCoords[0], gridCoords[1]) == -1:
						# Left clicking on an empty spot in the grid will add the character, if we haven't reached the size limit
						if partyCanvas.numberOfCharacters() < 2:
							partyCanvas.appendCharacter(selectedChar, 0, gridCoords[0], gridCoords[1])
					else:
						# Left clicking on a character in the grid will remove it
						partyCanvas.removeCharacter(gridCoords[0], gridCoords[1])

				elif event.button == RIGHT and gridCoords != (-1,-1):
					# Right clicking on a character in the grid will rotate them
					partyCanvas.rotateCharacterAt(gridCoords[0], gridCoords[1])

			if event.type == pygame.MOUSEMOTION:
				# Get the grid cell the mouse is hovering over, if any
				gridCoords = partyCanvas.screenToGridCoords(event.pos[0], event.pos[1])

				if gridCoords != (-1, -1):
					# Draw a preview of the character as they would appear if we placed them where the mouse is hovering
					if partyCanvas.numberOfCharacters() < 2:
						partyCanvas.previewCharacter(selectedChar, 0, gridCoords[0], gridCoords[1])

			partyCanvas.renderGrid(screen)

		# [SCENE] Actual Game
		elif current_scene == GAME_GRID:
			mapCanvas.update(event)
			mapCanvas.renderGrid(screen)

		pygame.display.flip()
