# -*- coding: utf-8 -*-

from cmath import inf
from random import randint
from players import Player
from actions import *
from board import Board
from math import inf


class RandomPlayer(Player):
    
    def __init__(self):
        super().__init__("Random player")

    def getNextMove(self, board: Board) -> Action:
        possibleMoves = Player.getPossibleMoves(self.player, board)
        return possibleMoves[randint(0, len(possibleMoves) - 1)]
