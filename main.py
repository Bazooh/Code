# -*- coding: utf-8 -*-
from board import *
from actions import *
from players import *
import randomplayer, conti_aymeric, aiplayer, aiplayer2, aiplayer3, players, aiplayer5
from generate_games import createAllRotatedXyWithX, boardToX, XToBoard

from time import time_ns

board = Board()
player1 = aiplayer2.AIPlayer()
player1.name = "player1 (%s)"%(player1.name)
player1.player = 1

player2 = conti_aymeric.AIPlayer()
player2.name = "player2 (%s)"%(player2.name)
player2.player = -1

current_player = 0
players = [player1, player2]

print(board)
print()
start2 = time_ns()
while not board.isTerminal():
    print("current player: %s"%(players[current_player].name))
    start = time_ns()
    action = players[current_player].getNextMove(board)
    execution_time = (time_ns()-start)/1_000_000_000.0
    action.apply(players[current_player].player, board)
    current_player = 1-current_player
    print(board)
    # print("value : " + str(player2.calcBoardValue(board, players[current_player].player)))
    # new_X, _ = createAllRotatedXyWithXy(boardToX(board, players[current_player].player), 0)
    # for x in new_X:
    #     print(XToBoard(x))
    if execution_time > 10:
        print(f"\033[91m\033[1mTemps d'execution: {execution_time} s\033[0m")
    else:
        print(f"Temps d'execution: {execution_time} s")
        
winner = board.getWinner()
if winner == player1.player:
    print(player1.name+" won")
elif winner == player2.player:
    print(player2.name+" won")
else:
    print("No winner")
