import torch.nn as nn
import torch
from generate_games import generateAGame
from aiplayer4 import AIPlayer as AIPlayerNetwork
from aiplayer5 import AIPlayer as AIPlayerCaseMultiplier
from randomplayer import RandomPlayer
from tqdm import tqdm
import matplotlib.pyplot as plt
from network import *
from board import Board
from save_neural_network import save_network

if __name__ == "__main__":

    X, y, boardScores = load_X_y('Code/X_y.txt')
    maxDuration = 0

    
    model = ModelEstimateBoard().to(device=DEVICE)
    model.load_state_dict(read_model_state_dict())
    
    losses = []
    print("Training model ...")
    for training in tqdm(range(100)):
        player1 = AIPlayerNetwork()
        player1.name = "player1 (%s) - (X)"%(player1.name)
        player1.player = 1

        player2 = AIPlayerNetwork()
        player2.name = "player2 (%s) - (O)"%(player2.name)
        player2.player = -1

        optimizer = torch.optim.SGD(model.parameters(), lr=LEARNING_RATE)
        
        duration = generateAGame(X, y, boardScores, [player1, player2], Board(), current_player_id=training%2, print_board=True, first_player_id=training%2)
        if duration > maxDuration: maxDuration = duration

        torchX, torchy = torch.tensor(X, device=DEVICE), torch.tensor(y, device=DEVICE)

        for epoch in tqdm(range(20)):
            pred_y = model(torchX)
            loss = LOSS_FUNCTION(pred_y, torchy)
            loss.backward()
            losses.append(loss.item())

            model.zero_grad()
            
            del loss
            del pred_y

            optimizer.step()

        save_network("Code/model_state_dict.json", model.state_dict())
        
        del torchX, torchy, player1, player2, optimizer
        torch.cuda.empty_cache()

        
    print(f"max duration of all games : {maxDuration:.3f}")
    save_X_y('Code/X_y.txt', X, y, boardScores)

    plt.plot(losses)
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.title("Learning rate %f"%(LEARNING_RATE))
    plt.show()
