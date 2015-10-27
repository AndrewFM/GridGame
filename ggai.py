# AI logic for the opponent(s)
class AIOpponent():
	import pygame

	def __init__(self):
		# ...
		nothing = 0

	def decideMoves(self, map):
		# Return a sequence of three moves
		import random
		moves = 3;
		
		# These variables define the move output format. Change as necessary.
		directions = ['UP','RIGHT','DOWN','LEFT']
		
		dir_seq = []
		for i in range(moves):
			dir = random.randrange(0,4)
			dir_seq += [directions[dir]]
		
		return dir_seq
