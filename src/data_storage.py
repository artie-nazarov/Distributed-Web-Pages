import os, json
from flask import jsonify
import concurrent.futures
import time
from multiprocessing.pool import ThreadPool

from clocks import new_clock
from utils import RepeatedTimer

# define
DATA_PATH = os.path.dirname(__file__) + "/.metadata/"
DATA_ENCODING = "iso-8859-1"
DATA_PERSISTANCE_PERIODICITY = 1  # in seconds

"""
TODO:
    1. Establish an eviction policy for in memory data
        - 4 MB?
    2. Connect to the frontend
        - How is data delivered to the frontend? (json object)
    3. Figure out file permissions
    5. Integrate SQL for storage
    6. Delete items from disk
"""

# DataStorage object is an interface for the storage system on each local node 
class DataStorage:
    def __init__(self, data={}, data_clocks={}, last_writer={}, owner="0.0.0.0"):
        self.data = data
        self.data_clocks = data_clocks
        self.last_writer = last_writer
        self.owner = owner
        # Launch disk persistance routine
        self.timer = RepeatedTimer(DATA_PERSISTANCE_PERIODICITY, self._persist_all_data)
    # Put raw data into memory
    def put(self, key, data, causal_metadata, last_writer):
        self.data[key] = data
        self.data_clocks[key] = causal_metadata
        self.last_writer[key] = last_writer

    # Get data for a given key
    def get(self, key, check_disk=False):
        # Check if data is stored in memory (most up-to date copy)
        if key in self.data:
            return dict(
                val=self.data[key],
                clock=self.data_clocks[key],
                last_writer=self.last_writer[key]
                )
        # Otherwise check on disk
        elif check_disk:
            return self._get_from_disk(key)

    # Search and get data from disk for a given key
    def _get_from_disk(self, key):
        file_name = f"{DATA_PATH}{key}.data"
        with open(file_name, 'r') as file:
            data = json.load(file)
        # Put the newly retrieved data into memory
        self.put(key, data['val'], data['data_clocks'], data['last_writer'])
        return data
    
    # Write all available data from memory to disk
    def _persist_all_data(self):
        with ThreadPool() as pool:
            for _ in pool.imap_unordered(self._persist_single_data, self.data.keys()):
                pass
    
    # Write a single data item to disk
    def _persist_single_data(self, key):
        file_name = f"{DATA_PATH}{key}.data"
        data = dict(
                val=self.data[key],
                clock=self.data_clocks[key],
                last_writer=self.last_writer[key]
                )
        jdata = json.dumps(data)
        with open(file_name, 'w') as file:
            file.write(jdata)

    # Retrieve data stored locally and put it onto the network
    def put_local_file(self, key, file_path):
        with open(file_path, 'rb') as file:
            data = file.read().decode(DATA_ENCODING)
            self.data[key] = data
            self.data_clocks[key] = new_clock(1)
            self.last_writer[key] = self.owner
