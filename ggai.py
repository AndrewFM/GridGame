import pygame
import random
import ggparty
import numpy as np
import copy
import ggmove
import time


# AI logic for the opponent(s)
class AIOpponent():
	
	def __init__(self):
		#Each entry in the action table is of the form [Number of moves-1][Row-Offset, Col-Offset, Facing Direction]
		#Sequence table is a parallel array with the cooresponding actions that results in the above offset/direction.
		self.action_table = [[],[],[]]
		self.sequence_table = [[],[],[]]
		for move1 in [ggparty.UP, ggparty.DOWN, ggparty.LEFT, ggparty.RIGHT]:
			trans = [0,0]
			trans = self.calcTranslate(trans, move1)
			self.action_table[0].append([trans[0],trans[1],move1])
			self.sequence_table[0].append([move1])

			for move2 in [ggparty.UP, ggparty.DOWN, ggparty.LEFT, ggparty.RIGHT]:
				trans = [0,0]
				trans = self.calcTranslate(trans, move1)
				trans = self.calcTranslate(trans, move2)
				self.action_table[1].append([trans[0],trans[1],move2])
				self.sequence_table[1].append([move1, move2])

				for move3 in [ggparty.UP, ggparty.DOWN, ggparty.LEFT, ggparty.RIGHT]:
					trans = [0,0]
					trans = self.calcTranslate(trans, move1)
					trans = self.calcTranslate(trans, move2)
					trans = self.calcTranslate(trans, move3)
					self.action_table[2].append([trans[0],trans[1],move3])
					self.sequence_table[2].append([move1, move2, move3])

	#Trans = [Row-offset, Col-offset], returns modification based on movement direction
	def calcTranslate(self, trans, direction):
		if direction == ggparty.UP:
			return [trans[0]+1, trans[1]]
		if direction == ggparty.DOWN:
			return [trans[0]-1, trans[1]]
		if direction == ggparty.LEFT:
			return [trans[0], trans[1]-1]
		if direction == ggparty.RIGHT:
			return [trans[0], trans[1]+1]

				
	# parties is a list of all ggparty.PartyGrid objects on the game board.
	# currentParty is your party.
	# all other allParties[i], where allParties[i] != currentParty are the opponent parties.
	# Basically, it uses brute force global search method
	def decideMoves(self, currentParty, allParties):
		# Return a sequence of three moves
		
		# Remember original locations and directions so they can be reset at end of simulation
		originLocations = []
		originDirections = []
		originHealth = []
		for i in range(len(allParties)):
			if allParties[i] == currentParty:
				curIndex = i
			originLocations.append([allParties[i].supergrid_location[0], allParties[i].supergrid_location[1]])
			originDirections.append(allParties[i].grid_angle)
			originHealth.append(allParties[i].health)

		bestAction = [0,0,0]
		for moveIndex in range(3):
			maxPayoff = -999
			for actIndex in range(len(self.action_table[moveIndex])):  # select AI's potential action
				# If we've already locked in an action, ignore all sequences that disagree with our intentions
				if moveIndex > 0 and self.sequence_table[moveIndex][actIndex][0] != bestAction[0]:
					continue
				if moveIndex > 1 and self.sequence_table[moveIndex][actIndex][1] != bestAction[1]:
					continue

				ggmove.setAbsolute(currentParty, [originLocations[curIndex][0]+self.action_table[moveIndex][actIndex][0]
												, originLocations[curIndex][1]+self.action_table[moveIndex][actIndex][1]]
												, self.action_table[moveIndex][actIndex][2], 0)
				payoff = 0			
				print(self.sequence_table[moveIndex][actIndex])
				
				for oppIndex in range(len(allParties)):
					if allParties[oppIndex] != currentParty:
						for oppActIndex in range(len(self.action_table[moveIndex])):
								ggmove.setAbsolute(allParties[oppIndex], [originLocations[oppIndex][0]+self.action_table[moveIndex][oppActIndex][0]
												, originLocations[oppIndex][1]+self.action_table[moveIndex][oppActIndex][1]]
												, self.action_table[moveIndex][oppActIndex][2], 0)
								ggmove.Move().attack(currentParty,allParties[oppIndex],[],0)
								ggmove.Move().attack(allParties[oppIndex],currentParty,[],0)
								damageTaken = originHealth[curIndex] - currentParty.health
								damageDealt = originHealth[oppIndex] - allParties[oppIndex].health
								payoff += damageDealt - damageTaken
								currentParty.health = originHealth[curIndex] # reset health totals after each test
								allParties[oppIndex].health = originHealth[oppIndex]						
				
				if payoff > maxPayoff:
					maxPayoff = payoff
					bestAction[moveIndex] = self.sequence_table[moveIndex][actIndex][moveIndex]

		# Reset parties to original locations and directions
		for i in range(len(allParties)):
			ggmove.setAbsolute(allParties[i], originLocations[i], originDirections[i], 1)

		dir_seq = bestAction
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
