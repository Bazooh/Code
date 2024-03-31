# from network import getXById
# from generate_games import XToBoard, boardToX
# from network import ModelEstimateBoard
# from aiplayer4 import AIPlayer
# import random
import torch


# print(getXById(0.13333333333333333, 0.4, 54785092075801085))
# this ensures that the current MacOS version is at least 12.3+
print(torch.backends.mps.is_available())
# this ensures that the current current PyTorch installation was built with MPS activated.
print(torch.backends.mps.is_built())
