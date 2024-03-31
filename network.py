import torch
import torch.nn as nn
from tqdm import tqdm
from generate_games import generateNGames, boardToX
from randomplayer import RandomPlayer
from save_neural_network import save_network
from collections import OrderedDict
import json

LEARNING_RATE = 0.1
LOSS_FUNCTION = nn.BCELoss()
DEVICE = torch.device("mps")

class ModelEstimateBoard(nn.Module):
    def __init__(self):
        super(ModelEstimateBoard, self).__init__()
        
        self.layer_1 = nn.Linear(60, 64)
        self.layer_2 = nn.Linear(64, 32)
        self.layer_3 = nn.Linear(32, 16)
        self.layer_out = nn.Linear(16, 1)
        
        self.relu = nn.ReLU()
        
    def forward(self, inputs):
        x = self.relu(self.layer_1(inputs))
        x = self.relu(self.layer_2(x))
        x = self.relu(self.layer_3(x))
        x = self.layer_out(x)
        x = torch.sigmoid(x)
        
        return x

def normalizeY(array):
    abs_array = [abs(elem[0]) for elem in array]
    
    array_diff = max(abs_array)
    
    print("normalizing y ...")
    for i in tqdm(range(len(array))):
        array[i][0] = ((array[i][0] / array_diff) + 1) / 2

def save_X_y(file_str: str, X: list, y: list, boardScores: list):
    file = open(file_str, 'w')

    print("Writting X and y in file ...")
    
    for i in tqdm(range(len(X))):
        XVal = 0
        file.write(str(float(X[i][0])) + " : " + str(float(X[i][1])) + " : ")
        for j in range(len(X[i]) - 2):
            XVal += int(X[i][j + 2]) << j
        file.write(str(XVal) + " : " + str(float(y[i][0])) + " : " + str(boardScores[0][i]) + " : " + str(boardScores[1][i]) + "\n")
    file.close()

def getXById(x0: float, x1: float, gameId: int):
    x = [x0, x1]
    for i in range(58):
        x.append(float(gameId % 2))
        gameId //= 2
    return x

def load_X_y(file_str: str):
    file = open(file_str)
    X, y, boardScores = [], [], [[], []]
    
    print("loading X and y ...")
    for line in tqdm(file.readlines()):
        if line == "": continue
        elif line[-1] == '\n':
            line = line[:-1]

        line = line.split(" : ")
        x0, x1, gameId, _y, boardScoreWhite, boardScoreBlack = float(line[0]), float(line[1]), int(line[2]), float(line[3]), int(line[4]), int(line[5])
        
        boardScores[0].append(boardScoreWhite)
        boardScores[1].append(boardScoreBlack)
        
        y.append([_y])
        X.append(getXById(x0, x1, gameId))
        
    file.close()
    return X, y, boardScores

def read_model_state_dict():
        file = open('Code/model_state_dict.json')
        json_str = file.read()
        file.close()
        
        data: OrderedDict = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(json_str)
        return OrderedDict(map(lambda kv: (kv[0], torch.tensor(kv[1])), data.items()))

if __name__ == "__main__":
    player1 = RandomPlayer()
    player1.name = "player1 (%s)"%(player1.name)
    player1.player = 1

    player2 = RandomPlayer()
    player2.name = "player2 (%s)"%(player2.name)
    player2.player = -1

    # X, y, boardScores = [], [], [[], []]
    # generateNGames(X, y, boardScores, n=1000, players=[player1, player2])
    # save_X_y('Code/X_y.txt', X, y, boardScores)
    
    X, y, boardScores = load_X_y('Code/X_y.txt')
    X, y = torch.tensor(X, device=DEVICE), torch.tensor(y, device=DEVICE)

    model = ModelEstimateBoard()
    model.to(device=DEVICE)
    model.load_state_dict(read_model_state_dict())
    optimizer = torch.optim.SGD(model.parameters(), lr=LEARNING_RATE)

    losses = []
    print("Training model ...")
    for epoch in tqdm(range(200)):
        optimizer.zero_grad()
        
        pred_y = model(X)
        loss = LOSS_FUNCTION(pred_y, y)
        losses.append(loss.item())

        loss.backward()

        optimizer.step()

    save_network("Code/model_state_dict.json", model.state_dict())

    import matplotlib.pyplot as plt
    plt.plot(losses)
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.title("Learning rate %f"%(LEARNING_RATE))
    plt.show()