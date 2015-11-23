import pygame
import random
import ggparty

# AI logic for the opponent(s)
class AIOpponent():
	
	def __init__(self, myID):
		self.myID = myID	   # An integer referring to the index of my party in the party array that will be passed to all the functions

	# parties is a list of all ggparty.PartyGrid objects on the game board.
	# parties[self.myID] is your party.
	# all other parties[i], where 0 <= i < len(parties), and i != self.myID are the opponent parties. 
	def decideMoves(self, parties):
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