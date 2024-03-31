# -*- coding: utf-8 -*-

from cmath import inf
from typing import List
from players import Player
from actions import *
from board import Board
from math import inf
from copy import deepcopy
from random import randint

def copyBoard(board: Board) -> Board:
    newBoard = Board()
    newBoard.__cells = deepcopy(board.cells)
    newBoard.__blackCount = board.blackMarbles
    newBoard.__whiteCount = board.whiteMarbles
    return newBoard

def generateRandomGameFromBoard(board: Board, player: int) -> int:
    board = copyBoard(board)
    
    def play(player: int):
        possibleMoves = Player.getPossibleMoves(player, board)
        rand = randint(0, len(possibleMoves) - 1)
        possibleMoves[rand].apply(player, board)
    
    i = 0
    while not board.isTerminal():
        play(player)
        player = -player
        i += 1
    
    return board.getWinner()

class AIPlayer(Player):
    """Artificial Intelligence based player"""

    def __init__(self):
        super().__init__("randomGenerate 0.1")
        self.__maxdepth = 4 #mettez ici la profondeur max de votre alpha beta en n'oubliant que vous devez répondre en 10s)

    def getNextMove(self, board: Board) -> Action:
        """Gets the next move to play"""
        return self.alphabeta(board)

    def heuristic(self, board:Board, playingPlayer: int) -> float:
        """Heuristic for alpha-beta, to be modified by the students"""
        if board.getTop() == self.player or board.getMarbleCount(-self.player) == 0:
            return inf
        elif board.getTop() == -self.player or board.getMarbleCount(self.player) == 0:
            return -inf
        
        numberOfRandomGameToPlay = 1
        winners = 0
        for i in range(numberOfRandomGameToPlay):
            winners += generateRandomGameFromBoard(board, playingPlayer)
        
        return winners / numberOfRandomGameToPlay

    def sortmoves(self, actionlist: List[Action]) -> List[Action]:
        """Sort the moves"""
        #As you noticed during the class, alpha beta performances depend on the order of the actions
        #if you feel it, you can sort the action list
        #by default, it is not
        return actionlist


    def alphabeta(self, board:Board) -> Action:
        """Decision made by alpha beta, returns the best action"""
        possiblemoves = self.sortmoves(Player.getPossibleMoves(self.player, board))
        if len(possiblemoves)==0:
            raise Exception("cannot have 0 possible play")
        elif len(possiblemoves)==1:
            return possiblemoves[0]
        else:
            best_score = -inf
            beta = inf
            coup = None
            for action in possiblemoves:
                action.apply(self.player, board)
                v = self.__minvalue(board, best_score, beta, 1)
                action.unapply(self.player, board)
                if v>best_score:
                    best_score = v
                    coup = action

            if coup == None:
                #we are going towards a defeat whatever the coup
                coup = possiblemoves[0]
            return coup

    def __maxvalue(self, board:Board, alpha:float, beta:float, depth:int) -> float:
        """For max nodes"""
        #terminal test
        if depth >= self.__maxdepth or board.isTerminal():
            return self.heuristic(board, self.player)
            
        v = -inf
        for action in Player.getPossibleMoves(self.player, board):            
            action.apply(self.player, board)
            v = max(v, self.__minvalue(board, alpha, beta, depth+1))
            action.unapply(self.player, board)
            if v>=beta:
                return v
            alpha = max(alpha,v)
        return v

    def __minvalue(self, board:Board, alpha:float, beta:float, depth:int) -> float:
        """For min nodes"""
        #terminal test
        if depth >= self.__maxdepth or board.isTerminal():
            return self.heuristic(board, -self.player)
            
        v = inf
        for action in Player.getPossibleMoves(-self.player,board):
            action.apply(-self.player, board)
            v = min(v, self.__maxvalue(board, alpha, beta, depth+1))
            action.unapply(-self.player, board)
            if v<=alpha:
                return v
            beta = min(beta,v)
        return v

