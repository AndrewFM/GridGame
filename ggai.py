import pygame
import random
import ggparty
import numpy as np
import copy
import ggmove


# AI logic for the opponent(s)
class AIOpponent():
	
	def __init__(self):
		# 0: 'UP'; 1: 'RIGHT'; 2: 'DOWN'; 3: 'LEFT'
		self.action_table = []
		for move1 in range(4):
			for move2 in range(4):
				for move3 in range(4):
					self.action_table.append([move1,move2,move3])
				
	# parties is a list of all ggparty.PartyGrid objects on the game board.
	# currentParty is your party.
	# all other allParties[i], where allParties[i] != currentParty are the opponent parties.
	# Basically, it uses brute force global search method
	def decideMoves(self, currentParty, allParties):
		# Return a sequence of three moves
		# import random
		# moves = 3;
		
		# These variables define the move output format. Change as necessary.
		directions = ['UP','RIGHT','DOWN','LEFT']
		
		maxPayoff = -999
		bestAction = [0,0,0]
		for selfAction in self.action_table:  # select AI's potential action	
			ghostSelf = copy.deepcopy(currentParty)
			for element in range(2):
				ghostSelf.party_members[element].src_image = currentParty.party_members[element].src_image
				ghostSelf.party_members[element].image = currentParty.party_members[element].image
			selfHP = ghostSelf.health
			payoff = 0
			
			print selfAction
			
			for opponent in allParties:
				if opponent!= currentParty:
					ghostOpponent = copy.deepcopy(opponent)
					for element in range(2):
						ghostOpponent.party_members[element].src_image = opponent.party_members[element].src_image
						ghostOpponent.party_members[element].image = opponent.party_members[element].image
					oppHP = ghostSelf.health
					for oppAction in self.action_table:
						for step in range(3):
							ggmove.Move().oneStep(ghostSelf,directions[selfAction[step]])
							ggmove.Move().oneStep(ghostOpponent,directions[oppAction[step]])
							ggmove.Move().attack(ghostSelf,ghostOpponent,[],0)
							ggmove.Move().attack(ghostOpponent,ghostSelf,[],0)
							damageTaken = selfHP - ghostSelf.health
							damageDealt = oppHP - ghostOpponent.health
							payoff += damageDealt - damageTaken
							ghostSelf.health = selfHP # reset health totals after each test
							ghostOpponent.health = oppHP
							
			
			if payoff > maxPayoff:
				maxPayoff = payoff
				bestAction = selfAction

		# dir = random.randrange(0,4)
		dir_seq = [ directions[ selfAction[0] ], directions[ selfAction[1] ], directions[ selfAction[2] ] ]
		return dir_seq
			
#			OccupyZone_self = []
#			AttackZones_self = []
#			AttackDirections_self = []
#			for move in range(3):
#				ggmove.Move().oneStep(ghostSelf,directions[action_table[i,move]])
#				OccupyZone_self.append([ghostSelf.getOccupyZone()])
#				AttackZones_self.append([ghostSelf.getAttackZones()]) # There might be more than one attack zones according to attack directions
#
#			for j in range( 0, len(parties) ):  # select an opponent party
#				if j != self.myID:
#					for k in range( 0, numActions ):  # select the opponent's potential action
#						OccupyZone_opponent = parties[j].getOccupyZone( action_table[k] )
#						AttackZones_opponent = parties[j].getAttackZones( action_table[k] )  # There might be more than one attack zones according to attack directions
#						AttackDirections_opponent = parties[j].getAttackDirectoins( action_table[k] )  # There might be more than one attack directions
#
#						for m in range(0, AttackDirections_self.shape[0]): # there could be more than one shooting directions from AI
#							AttackPoints += ( AttackZones_self[m] * OccupyZone_opponent ).sum()
#
#						for m in range(0, AttackDirections_opponent.shape[0]):  # there could be more than one shooting directions from opponent
#							DamagePoints += ( AttackZones_opponent[m] * OccupyZone_self ).sum()
#
#						F += AttackPoints - DamagePoints  # accumulate current benefit
#
#			if F > maxF:
#				maxF = F
#				action_index = i
#
#		# dir = random.randrange(0,4)
#		dir_seq = [ directions[ action_table[action_index][0] ], directions[ action_table[action_index][1] ], directions[ action_table[action_index][2] ] ]
#		return dir_seq

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
