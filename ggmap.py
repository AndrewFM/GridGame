# Data structure for the playing grid that the game takes place on.
import pygame
class MapGrid():

	def __init__(self, width, height):
		# This sets the WIDTH and HEIGHT of each grid location and the MARGIN between each cell
		self.WIDTH = width
		self.HEIGHT = height
		self.MARGIN = 5

		grid = [[0 for row in range(10)] for column in range(10)]

	def update(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			pos = pygame.mouse.get_pos()
			column = pos[0] / (self.WIDTH + self.MARGIN)
			row = pos[1] / (self.HEIGHT + self.MARGIN)
			grid[row][column] = 1

	# Renders the map on screen
	def renderGrid(self, screen):
		# Draw the grid
		for row in range(10):
			for column in range(10):
				color = (255,255,255)
				pygame.draw.rect(screen, color, [(self.MARGIN + self.WIDTH) * column + self.MARGIN, (self.MARGIN + self.HEIGHT) * row + self.MARGIN, self.WIDTH, self.HEIGHT])
