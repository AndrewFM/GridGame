import pygame
import ggparty

# Enums/Constants
#  -- Mouse Buttons
MOUSE_LEFT = 1
MOUSE_RIGHT = 3
#  -- Positioning
GRIDX = 50
GRIDY = 50
CHOICEX = 250
CHOICEY = 60
CHOICE_MARGIN = 40
CHOICE_RECT_MARGIN = 10

# Control for the "Create your party" scene.
class CreateParty():

	def __init__(self):
		self.previewAngle = ggparty.RIGHT
		self.partyCanvas = ggparty.PartyGrid()
		self.partyCanvas.gridPosition(GRIDX,GRIDY)
		self.selectedChar = ggparty.SINGLE_SHOT
		self.choiceSprite = [-1 for _ in range(3)]
		for i in range(3):
			self.choiceSprite[i] = ggparty.CharacterSprite((CHOICEX+i*(ggparty.CELL_SIZE+CHOICE_MARGIN),CHOICEY), ggparty.UP, i, 0)


	def update(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			# Get the grid cell that we clicked on
			gridCoords = self.partyCanvas.screenToGridCoords(event.pos[0], event.pos[1])

			if event.button == MOUSE_LEFT and gridCoords != (-1,-1):
				if self.partyCanvas.getCharacter(gridCoords[0], gridCoords[1]) == -1:
					# Left clicking on an empty spot in the grid will add the character, if we haven't reached the size limit
					if self.partyCanvas.numberOfCharacters() < 2:
						self.partyCanvas.appendCharacter(self.selectedChar, self.previewAngle, gridCoords[0], gridCoords[1])
				else:
					# Left clicking on a character in the grid will remove it
					self.partyCanvas.removeCharacter(gridCoords[0], gridCoords[1])

			elif event.button == MOUSE_LEFT:
				for i in range(3):
					# Left clicking on one of the characters in the choice list switches that to the active selected character
					bounds = self.__getChoiceBounds(i)
					mp = pygame.mouse.get_pos()
					if mp[0] > bounds[0] and mp[1] > bounds[1] and mp[0] < bounds[0]+bounds[2] and mp[1] < bounds[1]+bounds[3]:
						self.selectedChar = i
						break

			elif event.button == MOUSE_RIGHT and gridCoords != (-1,-1):
				# Right clicking on a character in the grid will rotate them
				success = self.partyCanvas.rotateCharacterAt(gridCoords[0], gridCoords[1])
				if success == 0:
					if self.partyCanvas.getCharacter(gridCoords[0], gridCoords[1]) == -1:
						self.previewAngle = (self.previewAngle + 90) % 360
						self.partyCanvas.previewCharacter(self.selectedChar, self.previewAngle, gridCoords[0], gridCoords[1])

			elif event.button == MOUSE_RIGHT:
				# Right clicking outside the party box simulates rotating the entire party (for debug purposes only, or maybe keep this?)
				self.partyCanvas.rotatePartyClockwise()

		if event.type == pygame.MOUSEMOTION:
			# Get the grid cell the mouse is hovering over, if any
			gridCoords = self.partyCanvas.screenToGridCoords(event.pos[0], event.pos[1])

			if gridCoords != (-1, -1):
				# Draw a preview of the character as they would appear if we placed them where the mouse is hovering
				if self.partyCanvas.numberOfCharacters() < 2:
					self.partyCanvas.previewCharacter(self.selectedChar, self.previewAngle, gridCoords[0], gridCoords[1])
			else:
				self.partyCanvas.clearGhosts()


	def __getChoiceBounds(self, charindex):
		charwidth = ggparty.CELL_SIZE
		if charindex == ggparty.SHIELD:
			charwidth = ggparty.CELL_SIZE*2
		return (CHOICEX-CHOICE_RECT_MARGIN+charindex*(ggparty.CELL_SIZE+CHOICE_MARGIN),
				CHOICEY-CHOICE_RECT_MARGIN,
				charwidth+CHOICE_RECT_MARGIN*2,
				ggparty.CELL_SIZE*2+CHOICE_RECT_MARGIN*2)

	def render(self, screen):
		self.partyCanvas.renderGrid(screen)
		for i in range(3):
			pygame.sprite.RenderPlain(self.choiceSprite[i]).draw(screen)
			if self.selectedChar == i:
				pygame.draw.rect(screen, ggparty.GRID_COLOR, self.__getChoiceBounds(i), 3)