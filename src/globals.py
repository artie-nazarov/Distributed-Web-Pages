from clocks import combine_clocks
from data_storage import *


# Global Data Storage
storage = DataStorage()

#dict that stores the most updated known clock for each value
known_clocks = {}

#list that stores the current view of the system
view = []

#int that stores the ID of the machine
id = -1

#address/ip
addr = ""

# Sharding information
total_shards = 1
shard_id = 1

def update_known_clocks(new_clocks):
    """Takes a dict of keys/clocks and updates known_clocks to include them"""
    for key, clock in new_clocks.items():
        if key not in known_clocks:
            known_clocks[key] = clock
        else:
            combine_clocks(known_clocks[key], clock)
