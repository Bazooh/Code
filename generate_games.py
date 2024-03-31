from board import Board
from randomplayer import RandomPlayer
from tqdm import tqdm
from torch import tensor
from players import Player
from random import randint
from time import time

ALPHA = 1.5

def XToBoard(X: list):
    board = Board()
    
    for i in range(15 - round(X[1]*15)): board.decreaseMarbleCount(-1)
    for i in range(15 - round(X[0]*15)): board.decreaseMarbleCount(1)
    for j in [2, 31]:
        for i in range(j, j + 29):
            if X[i] == 0.: continue

            if i - j <= 15:
                lev = 0
                col = (i - j) // 4
                row = (i - j) % 4
            elif i - j - 16 <= 8:
                lev = 1
                col = (i - j - 16) // 3
                row = (i - j - 16) % 3
            else:
                lev = 2
                col = (i - j - 25) // 2
                row = (i - j - 25) % 2
        
            board.setCell(1 if j == 2 else -1, lev, col, row)
    return board

def boardToX(board: Board, playerTurn: int):
    X = [0. for _ in range(60)]
    X[0] = float(board.whiteMarbles / 15) if playerTurn == 1 else float(board.blackMarbles / 15)
    X[1] = float(board.blackMarbles / 15) if playerTurn == 1 else float(board.whiteMarbles / 15)
    
    i = 2
    for lev in range(3):
        for line in range(4 - lev):
            for col in range(4 - lev):
                piece = board.getCell(lev, line, col)*playerTurn
                if piece == 1:
                    X[i] = 1.
                elif piece == -1:
                    X[i + 29] = 1.
                i += 1
    return X

def boardScoreToY(boardScoreWhite: int, boardScoreBlack: int) -> float:
    x, y = boardScoreWhite, boardScoreBlack
    return (2*x - (x - y)*(ALPHA**(-x - y))) / (2*(x + y))

def createAllRotatedXyWithX(X: list):
    new_X = []
    
    def symetricX(X: list):
        X_o = [x for x in X]
        for j in [2, 31]:
            for i in range(j, j + 29):
                if i - j <= 15:
                    col = (i - j) // 4
                    row = (i - j) % 4
                    X_o[i] = X[j + 4*row + col]
                elif i - j - 16 <= 8:
                    col = (i - j - 16) // 3
                    row = (i - j - 16) % 3
                    X_o[i] = X[j + 16 + 3*row + col]
                else:
                    col = (i - j - 25) // 2
                    row = (i - j - 25) % 2
                    X_o[i] = X[j + 25 + 2*row + col]
        
        return X_o
    
    def rotateX(X: list):
        X_o = [x for x in X]
        for j in [2, 31]:
            for i in range(j, j + 29):
                if i - j <= 15:
                    col = (i - j) // 4
                    row = (i - j) % 4
                    X_o[i] = X[j + 4*row + 3 - col]
                elif i - j - 16 <= 8:
                    col = (i - j - 16) // 3
                    row = (i - j - 16) % 3
                    X_o[i] = X[j + 16 + 3*row + 2 - col]
                else:
                    col = (i - j - 25) // 2
                    row = (i - j - 25) % 2
                    X_o[i] = X[j + 25 + 2*row + 1 - col]
        
        return X_o
    
    for i in range(4):
        for j in range(2):
            new_X.append(X)
            X = symetricX(X)
        X = rotateX(X)
    
    return new_X

def are3DMatrixEquals(A, B):
    for i in range(len(A)):
        for j in range(len(A[i])):
            for k in range(len(A[i][j])):
                if A[i][j][k] != B[i][j][k]:
                    return False
    return True

def playAction(player: Player, board: Board, boardsPlayedThisGame):
    action = player.getNextMove(board)
    action.apply(player.player, board)
    
    for boardPlayed in boardsPlayedThisGame:
        if are3DMatrixEquals(boardPlayed, board.cells):
            action.unapply(player.player, board)
            actionsPossible = Player.getPossibleMoves(player.player, board)
            action = actionsPossible[randint(0, len(actionsPossible) - 1)]
            action.apply(player.player, board)
    
    boardsPlayedThisGame.append(board.cells)

def updateXy(X: list, new_X: list, y: list, boardScores: list, new_boardScores: list):
    for i in range(len(new_X)):
        try:
            xIndex = X.index(new_X[i])
        
        except ValueError:
            X.append(new_X[i])
            boardScores[0].append(new_boardScores[0][i])
            boardScores[1].append(new_boardScores[1][i])
            y.append([boardScoreToY(new_boardScores[0][i], new_boardScores[1][i])])
        
        else:
            boardScores[0][xIndex] += new_boardScores[0][i]
            boardScores[1][xIndex] += new_boardScores[1][i]
            y[xIndex][0] = boardScoreToY(boardScores[0][xIndex], boardScores[1][xIndex])

def generateAGame(X: list, y: list, boardScores: list, players: list, board: Board, boardsPlayedThisGame = [], current_player_id = 0, print_board = False, first_player_id = 0):
    new_X = []
    maxDuration = 0
    duration = 0

    
    while not board.isTerminal():
        if print_board:
            print("current player: %s"%(players[current_player_id].name))

        startTime = time()

        playAction(players[current_player_id], board, boardsPlayedThisGame)

        if startTime:
            duration = time() - startTime
            if duration > maxDuration: maxDuration = duration

        current_player_id = 1-current_player_id
        new_X.append(boardToX(board, players[current_player_id].player))
        if print_board:
            print(board)
            print(players[1].calcBoardValue(board, players[current_player_id].player)*players[current_player_id].player)
            print(f"duration : {duration:.2f}")
    
    scoreWhite = board.whiteMarbles if board.whiteMarbles < 4 else 4
    scoreBlack = board.blackMarbles if board.blackMarbles < 4 else 4
    
    scores = {1: scoreWhite, -1: scoreBlack}
    
    all_X, all_scores = [], [[], []]
    
    for i, new_x in enumerate(new_X):
        all_X += createAllRotatedXyWithX(new_x)
        
        if i % 2 == 0:
            all_scores[0] += 8*[scores[-players[first_player_id].player]]
            all_scores[1] += 8*[scores[ players[first_player_id].player]]
        else:
            all_scores[0] += 8*[scores[ players[first_player_id].player]]
            all_scores[1] += 8*[scores[-players[first_player_id].player]]
    
    updateXy(X, all_X, y, boardScores, all_scores)
    if print_board:
        print(f"max duration of the game : {maxDuration:.3f}")
    return maxDuration

def generateAGameWithFirstCoupRandom(X: list, y: list, boardScores: list, players: list, board: Board, nbRandomCoupPerPlayer: int = 0, current_player_id: int = 0, first_player_id: int = 0):
    player = RandomPlayer()
    boardsPlayedThisGame = []

    for i in range(2*nbRandomCoupPerPlayer):
        if board.isTerminal():
            return
        
        player.player = 1 if current_player_id == 0 else -1
        playAction(player, board, boardsPlayedThisGame)
        current_player_id = 1-current_player_id
    
    return generateAGame(X=X, y=y, boardScores=boardScores, players=players, board=board, boardsPlayedThisGame=boardsPlayedThisGame, current_player_id=current_player_id, first_player_id=first_player_id)

def generateNGames(X: list, y: list, boardScores: list, n: int, players: list, nbRandomCoupPerPlayer: int = 0):
    print("Generating games...")
    for i in tqdm(range(n)):
        generateAGameWithFirstCoupRandom(X, y, boardScores, players, Board(), nbRandomCoupPerPlayer=nbRandomCoupPerPlayer, current_player_id=i%2, first_player_id=i%2)