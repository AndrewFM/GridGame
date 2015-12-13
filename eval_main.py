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
		mapScene.addPartyToMap(aiPlayers[i],ggparty.UP,starts[i+1][0],starts[i+1][1])
		aiPlayers[i].grid_color = ggparty.RED
		aiPlayers[i].maxHealth()

	# Game Loop
	while True:
		alivePlayers = [x for x in aiPlayers if x.alive == 1]
		numAlive = len(alivePlayers)
		if numAlive == 0: # tie; all dead
			return None
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

# loop to run a bunch of games; TODO actually vary agents, collect meaningful data
for j in range(10):
	aiPlayers = []
	stats = {}
	for i in range(4):
	 	aiPlayers.append(ggai.constructParty())
	 	aiPlayers[i].assignAI(ggai.AIOpponent())
	winner = runGame(aiPlayers)
	if winner is not None:
		pass # TODO based on features of winner increment win counters of stats dict

