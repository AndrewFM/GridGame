# The main file which should be run in order to launch the game.
from pygame.locals import *
import pygame
import ggcreateparty
import ggmap
import ggparty
import ggai

# Enums/Constants
#  -- Scenes
CREATE_PARTY = 1
GAME_GRID = 2
global GGEVAL
GGEVAL = True

def runGame(AIsToRun): # AIsToRun: list of AI players; returns the winner, or None if tie

	# Game Initialization
	running = True
	partyScene = -1
	#pygame.init()
	event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN) # probably not necessary since I have to modify ggmap anyway
	mapScene = ggmap.MapGrid(12,12)
	NUM_AI_PLAYERS = len(AIsToRun)
	starts = [[0,0],
			[ggmap.GRID_SIZE-3,ggmap.GRID_SIZE-3],
			[ggmap.GRID_SIZE-3,0],
			[0,ggmap.GRID_SIZE-3]]
	step = 0
			
	# Initialize text outputs
	currentalert = []

	huPlayer = None
	aiPlayers = AIsToRun
	# for i in range(NUM_AI_PLAYERS):
	# 	aiPlayers.append(ggai.constructParty())
	# 	aiPlayers[i].assignAI(ggai.AIOpponent())

	for i in range(NUM_AI_PLAYERS):
		mapScene.addPartyToMap(aiPlayers[i],ggparty.UP,starts[i][0],starts[i][1])
		aiPlayers[i].grid_color = ggparty.RED
		aiPlayers[i].maxHealth()

	# Game Loop
	for asdf in xrange(300):
		for a in aiPlayers:
			print a.supergrid_location, a.health, '\n'
		alivePlayers = [x for x in aiPlayers if x.alive == 1]
		print alivePlayers
		numAlive = len(alivePlayers)
		if numAlive == 0: # tie; all dead
			return 'tie'
		elif numAlive == 1:
			winner = alivePlayers[0] # last bot standing
			return winner

		mapScene.executeStep(None, None, aiPlayers, step)
		step += 1
		
		if step >= 3: # If we've done all 3 steps, end the execution phase
			step = 0
			mapScene.exe = 0

		for currentAI in aiPlayers:
			if currentAI.health <= 0:
				currentAI.alive = 0
				currentAI.supergrid_location = [-10,-10]
	return 'time up'

# loop to run a bunch of games; TODO actually vary agents, collect meaningful data
def runExperiment(aiTypes, n):
	j = 0
	while j < n:
		aiPlayers = []
		stats = []
		for t in aiTypes:
		 	aiPlayers.append(ggai.constructParty())
		 	if t[0][0] == 'd':
		 		ai = ggai.AIOpponent(t[1], t[2])
		 	elif t[0][0] == 'n':
		 		ai = ggai.AIOpponent_nondeterministic(t[1], t[2])
		 	aiPlayers[-1].trust = [0]*len(aiTypes)
		 	aiPlayers[-1].assignAI(ai)
		winner = runGame(aiPlayers)
		if winner != 'time up':
			if winner == 'tie':
				stats.append('tie')
				j += 1
				continue
			at = 'd' if isinstance(winner, ggai.AIOpponent) else 'n'
			stats.append({'type': at, 'attack_metric': winner.ai_control.attack_metric, 'defend_metric': winner.ai_control.defend_metric})
			j += 1
	return stats

