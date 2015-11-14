import pygame
import ggparty
import ggutils

# Enums/Constants
#  -- Mouse Buttons
MOUSE_LEFT = 1
MOUSE_RIGHT = 3
#  -- Colors
INACTIVE_COLOR = (180,180,180)
UI_COLOR = ggparty.BLACK
#  -- Positioning
GRIDX = 170
GRIDY = 200
CHOICEX = 400
CHOICEY = 210
CHOICE_MARGIN = 40
CHOICE_RECT_MARGIN = 10
TITLEX = 400
TITLEY = 120
DESC_MARGIN = 20
FINISH_BUTTON_BOUNDS = (325,350,150,50) 

# Control for the "Create your party" scene.
class CreateParty():

	def __init__(self):
		self.previewAngle = ggparty.RIGHT
		self.partyCanvas = ggparty.PartyGrid()
		self.partyCanvas.gridPosition(GRIDX,GRIDY)
		self.selectedChar = ggparty.SINGLE_SHOT
		self.finishPressed = 0
		self.choiceSprite = [-1 for _ in range(3)]
		for i in range(3):
			self.choiceSprite[i] = ggparty.CharacterSprite((CHOICEX+i*(ggparty.CELL_SIZE+CHOICE_MARGIN),CHOICEY), ggparty.UP, i, 0)

		self.fontTitle = pygame.font.SysFont("Verdana", 28, bold=1)
		self.fontBasic =  pygame.font.SysFont("Verdana", 14)
		self.strTitle = self.fontTitle.render("Construct Your Party", 1, UI_COLOR)
		self.strCharDesc = []
		self.strCharDesc.append(self.fontBasic.render("Shoots in one direction, adds 2 health points.", 0, UI_COLOR))
		self.strCharDesc.append(self.fontBasic.render("Shoots in two directions, adds 1 health point.", 0, UI_COLOR))
		self.strCharDesc.append(self.fontBasic.render("Cannot shoot at all, adds 5 health points.", 0, UI_COLOR))
		self.strButton = []
		self.strButton.append(self.fontBasic.render("Two Remaining", 0, INACTIVE_COLOR))
		self.strButton.append(self.fontBasic.render("One Remaining", 0, INACTIVE_COLOR))
		self.strButton.append(self.fontBasic.render("Finish", 0, UI_COLOR))


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
				mp = pygame.mouse.get_pos()
				for i in range(3):
					# Left clicking on one of the characters in the choice list switches that to the active selected character
					bounds = self.__getChoiceBounds(i)
					if ggutils.pointInRect(mp,bounds) == 1:
						self.selectedChar = i
						break

				if ggutils.pointInRect(mp,FINISH_BUTTON_BOUNDS) == 1:
					if self.partyCanvas.numberOfCharacters() == 2:
						self.finishPressed = 1

			elif event.button == MOUSE_RIGHT and gridCoords != (-1,-1):
				# Right clicking on a character in the grid will rotate them
				success = self.partyCanvas.rotateCharacterAt(gridCoords[0], gridCoords[1])
				if success == 0 and self.partyCanvas.numberOfCharacters() < 2:
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


	# Gets the rectangular boundaries of each of the characters in the selection menu
	def __getChoiceBounds(self, charindex):
		charwidth = ggparty.CELL_SIZE
		if charindex == ggparty.SHIELD:
			charwidth = ggparty.CELL_SIZE*2
		return (CHOICEX-CHOICE_RECT_MARGIN+charindex*(ggparty.CELL_SIZE+CHOICE_MARGIN),
				CHOICEY-CHOICE_RECT_MARGIN,
				charwidth+CHOICE_RECT_MARGIN*2,
				ggparty.CELL_SIZE*2+CHOICE_RECT_MARGIN*2)

	# Returns the constructed party when the player is finished making their party and has pressed the finish button. -1 otherwise.
	# Used to "propagate" the message up to the main.py file so that it knows to swich to the next scene.
	def isFinished(self):
		if self.finishPressed == 1:
			return self.partyCanvas
		else:
			return -1

	def render(self, screen):
		# Title Text
		screen.blit(self.strTitle, (TITLEX-(self.strTitle.get_width()/2), TITLEY))

		# Selected Character Description
		screen.blit(self.strCharDesc[self.selectedChar], 
			((self.__getChoiceBounds(0)[0]+self.__getChoiceBounds(2)[0]+self.__getChoiceBounds(2)[2])/2-self.strCharDesc[self.selectedChar].get_width()/2
			, CHOICEY+ggparty.CELL_SIZE*2+CHOICE_RECT_MARGIN+DESC_MARGIN))

		# Party Grid
		self.partyCanvas.renderGrid(screen)

		# Character Selection
		for i in range(3):
			pygame.sprite.RenderPlain(self.choiceSprite[i]).draw(screen)
			if self.selectedChar == i:
				pygame.draw.rect(screen, UI_COLOR, self.__getChoiceBounds(i), 3)

		# Finish Button
		pygame.draw.rect(screen, UI_COLOR, FINISH_BUTTON_BOUNDS, 3)
		buttonText = self.strButton[self.partyCanvas.numberOfCharacters()]
		screen.blit(buttonText, 
			(FINISH_BUTTON_BOUNDS[0]+FINISH_BUTTON_BOUNDS[2]/2-buttonText.get_width()/2
				,FINISH_BUTTON_BOUNDS[1]+FINISH_BUTTON_BOUNDS[3]/2-buttonText.get_height()/2))
