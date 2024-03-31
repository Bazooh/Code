# -*- coding: utf-8 -*-

from cmath import inf
from typing import List
from players import Player
from actions import *
from board import Board
from math import inf

class AIPlayer(Player):
    """Artificial Intelligence based player"""

    def __init__(self):
        super().__init__("caseMultiplier 0.1")
        self.__maxdepth = 4 #mettez ici la profondeur max de votre alpha beta en n'oubliant que vous devez répondre en 10s)

    def getNextMove(self, board: Board) -> Action:
        """Gets the next move to play"""
        return self.alphabeta(board)

    def heuristic(self, board:Board) -> float:
        """Heuristic for alpha-beta, to be modified by the students"""
        if board.getTop() == self.player or board.getMarbleCount(-self.player) == 0:
            return inf
        elif board.getTop() == -self.player or board.getMarbleCount(self.player) == 0:
            return -inf
        
        def caseMultiplier(lev, line, col):
            
            lev0_middle = 0.15
            lev0_outter = 0.02
            lev1_middle = 0.08
            lev1_outter = 0.05
            lev2 = 0.1
            
            multiplcator = 2 if Action._canBeMoved(board, lev, line, col) else 1
            
            if lev == 0:
                if line == 0 or line == 3 or col == 0 or col == 3:
                    return lev0_outter * multiplcator
                return lev0_middle * multiplcator
            if lev == 1:
                if line == 0 or line == 2 or col == 0 or col == 2:
                    return lev1_outter * multiplcator
                return lev1_middle * multiplcator
            return lev2 * multiplcator
        
        value = 0
        
        for lev in range(3):
            for line in range(4 - lev):
                for col in range(4 - lev):
                    value += board.getCell(lev, line, col) * self.player * caseMultiplier(lev, line, col)
        
        value += board.getMarbleCount(self.player) - board.getMarbleCount(-self.player)
        
        return value

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
            return self.heuristic(board)
            
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
            return self.heuristic(board)
            
        v = inf
        for action in Player.getPossibleMoves(-self.player,board):
            action.apply(-self.player, board)
            v = min(v, self.__maxvalue(board, alpha, beta, depth+1))
            action.unapply(-self.player, board)
            if v<=alpha:
                return v
            beta = min(beta,v)
        return v

