import pygame
import ggparty

# Enums/Constants
#  -- Mouse Buttons
MOUSE_LEFT = 1
MOUSE_RIGHT = 3

# Control for the "Create your party" scene.
class CreateParty():

	def __init__(self):
		self.previewAngle = ggparty.RIGHT
		self.partyCanvas = ggparty.PartyGrid()
		self.partyCanvas.gridPosition(25,25)
		self.selectedChar = ggparty.SINGLE_SHOT


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

			elif event.button == MOUSE_RIGHT and gridCoords != (-1,-1):
				# Right clicking on a character in the grid will rotate them
				success = self.partyCanvas.rotateCharacterAt(gridCoords[0], gridCoords[1])
				if success == 0:
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


	def render(self, screen):
		self.partyCanvas.renderGrid(screen)