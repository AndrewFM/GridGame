import pygame
import random
import ggparty
import numpy as np
import copy
import ggmove

MODE_OFFENSE = 0
MODE_DEFENSE = 1

#Each of the metric functions return an array containing the following respective elements:
#	[Party to target, that party's value of metric, min value of metric, max value of metric]
#   The latter three values are for any normalization of the metrics that may need to be done.
#
#The mode argument determines whether we are considering attacking or defending against the returned party (should be MODE_OFFENSE/MODE_DEFENSE).
#The meta argument is an array of two elements [[list of trust values], last party attacked by].

# Generic logic shared by all the metric functions -- you can ignore this if you aren't writing your own metric functions.
def __metric_generic(opponentParties, opponentValues, minVal, maxVal, mode, minmodes, maxmodes):
	if mode in minmodes:
		retValue = maxVal+1
		for i in range(len(opponentParties)):
			variable = opponentValues[i]
			if variable < retValue:
				retParty = opponentParties[i]
				retValue = variable
	else:
		retValue = minVal-1
		for i in range(len(opponentParties)):
			variable = opponentValues[i]
			if variable > retValue:
				retParty = opponentParties[i]
				retValue = variable	
	return [retParty, retValue, minVal, maxVal]	

#Determines a party in terms of your distance to them
#	MODE_OFFENSE: Returns closest party
#	MODE_DEFENSE: Returns closest party
def metric_distance(allParties, myParty, mode):
	opponentParties = [party for party in allParties if party != myParty]
	return __metric_generic(opponentParties, [min(abs(party.supergrid_location[0]-myParty.supergrid_location[0]),
												  abs(party.supergrid_location[1]-myParty.supergrid_location[1])) for party in opponentParties], 0, 10, mode, [MODE_OFFENSE, MODE_DEFENSE], [])

#Determines a party in terms of their remaining health
#	MODE_OFFENSE: Returns party with least health
#	MODE_DEFENSE: Returns party with most health
def metric_health(allParties, myParty, mode):
	opponentParties = [party for party in allParties if party != myParty]
	return __metric_generic(opponentParties, [party.health for party in opponentParties], 0, 100, mode, [MODE_OFFENSE], [MODE_DEFENSE])

#Determines a party in terms of their firepower.
#	MODE_OFFENSE: Returns party with least firepower
#	MODE_DEFENSE: Returns party with most firepower
def metric_threat(allParties, myParty, mode):
	opponentParties = [party for party in allParties if party != myParty]
	values = []
	for party in opponentParties:
		threat = 0
		for char in party.party_members:
			if char.chartype == ggparty.SINGLE_SHOT:
				threat += 1
			elif char.chartype == ggparty.DOUBLE_SHOT:
				threat += 2
		values.append(threat)
	return __metric_generic(opponentParties, values, 1, 4, mode, [MODE_OFFENSE], [MODE_DEFENSE])

#Determines a party in terms of their amount of vulnerable surface area.
#	MODE_OFFENSE: Returns party with most surface area
#	MODE_DEFENSE: Returns party with least surface area
def metric_ease(allParties, myParty, mode):
	opponentParties = [party for party in allParties if party != myParty]
	values = []
	for party in opponentParties:
		surface = 0
		for char in party.party_members:
			if char.chartype == ggparty.SINGLE_SHOT:
				surface += 2
			elif char.chartype == ggparty.DOUBLE_SHOT:
				surface += 3
			else:
				surface += 4
		values.append(surface)
	return __metric_generic(opponentParties, values, 4, 7, mode, [MODE_DEFENSE], [MODE_OFFENSE])

#Determines a party in terms of their level of trust
#	MODE_OFFENSE: Returns the least trusted party
#	MODE_DEFENSE: Returns the most trusted party
def metric_trust(allParties, myParty, mode):
	opponentParties = [party for party in allParties if party != myParty]
	trustValues = []
	for i in range(len(allParties)):
		if allParties[i] != myParty:
			trustValues.append(myParty.trust[i])
	return __metric_generic(opponentParties, 0, -5, 5, mode, [MODE_OFFENSE], [MODE_DEFENSE])

#Gives the party that attacked you most recently
#	MODE_OFFENSE & MODE_DEFENSE both return the same party.
def metric_agro(allParties, myParty, mode):
	opponentParties = [party for party in allParties if party != myParty]
	if myParty.last_attacker == -1:
		myParty.last_attacker = random.choice(opponentParties)
	return myParty.last_attacker

class AIOpponent_nondeterministic():
	#Attack metric & defend metric should be pointers to one of the metric functions above.
	def __init__(self, attack_metric, defend_metric):
		#Each entry in the action table is of the form [Number of moves-1][Row-Offset, Col-Offset, Facing Direction]
		#Sequence table is a parallel array with the cooresponding actions that results in the above offset/direction.
		self.move_obj = ggmove.Move()
		self.action_table = [[],[],[]]
		self.sequence_table = [[],[],[]]
		self.attack_metric = attack_metric
		self.defend_metric = defend_metric
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

		targetPriority = [1]*len(allParties)
		
		bestAction = [0,0,0]
		for moveIndex in range(3):
			maxPayoffs = [-999, -999] # [0] is best action, [1] is second best
			currentBestActions = [-1,-1] # [0] is best action, [1] is second best
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
				
				for oppIndex in range(len(allParties)):
					#Don't target self, and don't target parties that are already dead
					if allParties[oppIndex] != currentParty and allParties[oppIndex].health > 0:
						for oppActIndex in range(len(self.action_table[moveIndex])):
								ggmove.setAbsolute(allParties[oppIndex], [originLocations[oppIndex][0]+self.action_table[moveIndex][oppActIndex][0]
												, originLocations[oppIndex][1]+self.action_table[moveIndex][oppActIndex][1]]
												, self.action_table[moveIndex][oppActIndex][2], 0)
								self.move_obj.attack(currentParty,allParties[oppIndex],[],0)
								self.move_obj.attack(allParties[oppIndex],currentParty,[],0)
								damageTaken = originHealth[curIndex] - currentParty.health
								damageDealt = originHealth[oppIndex] - allParties[oppIndex].health
								r=float(float(currentParty.health)/float(currentParty.healthRecord[0]))
								#print r
								if(r>0.8):
									currentParty.atkweight=2
									currentParty.defweight=1
								elif(r>0.5 and r<0.8):
									currentParty.atkweight=1
									currentParty.defweight=1
								else:
									currentParty.atkweight=1
									currentParty.defweight=2 
								payoff += currentParty.atkweight*targetPriority[oppIndex]*damageDealt - currentParty.defweight*damageTaken
								currentParty.health = originHealth[curIndex] # reset health totals after each test
								allParties[oppIndex].health = originHealth[oppIndex]						
				
				if payoff > maxPayoffs[0]:
					maxPayoffs[1] = maxPayoffs[0]
					maxPayoffs[0] = payoff
					currentBestActions[1] = currentBestActions[0]
					currentBestActions[0] = self.sequence_table[moveIndex][actIndex][moveIndex]
				elif payoff > maxPayoffs[1]:
					maxPayoffs[1] = payoff
					currentBestActions[1] = self.sequence_table[moveIndex][actIndex][moveIndex]
			
			bestAction[moveIndex] = currentBestActions[random.getrandbits(1)]
			
		# Reset parties to original locations and directions
		for i in range(len(allParties)):
			ggmove.setAbsolute(allParties[i], originLocations[i], originDirections[i], 1)

		dir_seq = bestAction
		return dir_seq

# AI logic for the opponent(s)
class AIOpponent():
	
	def __init__(self, attack_metric, defend_metric):
		#Each entry in the action table is of the form [Number of moves-1][Row-Offset, Col-Offset, Facing Direction]
		#Sequence table is a parallel array with the cooresponding actions that results in the above offset/direction.
		self.move_obj = ggmove.Move()
		self.action_table = [[],[],[]]
		self.sequence_table = [[],[],[]]
		self.attack_metric = attack_metric
		self.defend_metric = defend_metric
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
			
		targetPriority = [1]*len(allParties)
		
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
				
				for oppIndex in range(len(allParties)):
					#Don't target self, and don't target parties that are already dead
					if allParties[oppIndex] != currentParty and allParties[oppIndex].health > 0:
						for oppActIndex in range(len(self.action_table[moveIndex])):
								ggmove.setAbsolute(allParties[oppIndex], [originLocations[oppIndex][0]+self.action_table[moveIndex][oppActIndex][0]
												, originLocations[oppIndex][1]+self.action_table[moveIndex][oppActIndex][1]]
												, self.action_table[moveIndex][oppActIndex][2], 0)
								self.move_obj.attack(currentParty,allParties[oppIndex],[],0)
								self.move_obj.attack(allParties[oppIndex],currentParty,[],0)
								damageTaken = originHealth[curIndex] - currentParty.health
								damageDealt = originHealth[oppIndex] - allParties[oppIndex].health
								r=float(float(currentParty.health)/float(currentParty.healthRecord[0]))
								#print currentParty.health
								#print currentParty.healthRecord[0]
								print r
								if(r>0.8):
									currentParty.atkweight=2
									currentParty.defweight=1
								elif(r>0.5 and r<0.8):
									currentParty.atkweight=1
									currentParty.defweight=1
								else:
									currentParty.atkweight=1
									currentParty.defweight=2 
								payoff += currentParty.atkweight*targetPriority[oppIndex]*damageDealt - currentParty.defweight*damageTaken
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
