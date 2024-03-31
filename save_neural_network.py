import json
from collections import OrderedDict


def save_network(file_str, network):
    file = open(file_str, 'w')
    
    data = OrderedDict(map(lambda kv: (kv[0], kv[1].tolist()), network.items()))
    
    file.write(json.dumps(data))
    
    file.close()