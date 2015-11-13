import pygame
import random
import ggparty

# AI logic for the opponent(s)
class AIOpponent():
	
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

# Return a constructed party with two characters.
# For now, this is generating a randomish party, however...
# TODO: Construct the party intelligently using AI methods
def constructParty():
	newParty = ggparty.PartyGrid()

	while newParty.numberOfCharacters() < 2:
		chartype = random.choice([ggparty.SINGLE_SHOT, ggparty.DOUBLE_SHOT, ggparty.SHIELD])
		direction = random.choice([ggparty.UP, ggparty.DOWN, ggparty.LEFT, ggparty.RIGHT])

		if chartype == ggparty.SHIELD:
			newParty.appendCharacter(chartype, direction, random.choice(range(0,2)), random.choice(range(0,2)))
		else:
			newParty.appendCharacter(chartype, direction, random.choice(range(0,3)), random.choice(range(0,3)))

	return newParty