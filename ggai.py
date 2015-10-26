# AI logic for the opponent(s)
class AIOpponent():
import pygame
import math

	def __init__(self):
		# ...

	def decideMoves(self, map):
		# Return a sequence of three moves
		import random
		moves = 3;
		
		# These variables define the move output format. Change as necessary.
		directions = ['up','right','down','left']
		
		dir_seq = []
		for i in range(moves):
			dir = random.randrange(0,3,1)
			dir_seq += [directions[dir]]
		
		return dir_seq
		
		# Return a sequence of three moves
