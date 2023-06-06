import os, json
from flask import jsonify
import concurrent.futures
import time
from multiprocessing.pool import ThreadPool
import sqlite3
from sqlite3 import Error
import hashlib
import math

from clocks import new_clock
from utils import RepeatedTimer
from pathlib import Path

Path(os.path.dirname(__file__)+"/.metadata").mkdir(exist_ok=True)
# define
DATA_PATH = os.path.dirname(__file__) + "/.metadata/"
DATA_ENCODING = "iso-8859-1"
DATA_PERSISTANCE_PERIODICITY = 10  # in seconds

"""
TODO:
    1. Establish an eviction policy for in memory data
    2. Delete items from disk
"""
# SQLite database functionality

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path, check_same_thread=False)
        # The Data Base capacity is 1 GB
        connection.cursor().execute('PRAGMA page_size = 1000000000')
    except Error as e:
        raise e
    return connection

def execute_query(connection, query, data=None):
    cursor = connection.cursor()
    try:
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        connection.commit()
    except Error as e:
        raise e
    
def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        raise e

# DataStorage object is an interface for the storage system on each local node 
class DataStorage:
    def __init__(self, data={}, data_clocks={}, last_writer={}, owner="0.0.0.0"):
        self.data = data
        self.data_clocks = data_clocks
        self.last_writer = last_writer
        self.owner = owner
        # Launch disk persistance routine
        #self.timer = RepeatedTimer(DATA_PERSISTANCE_PERIODICITY, self._persist_all_data)
        # Set up SQL database
        self.db_connection = create_connection(DATA_PATH+"data_storage.db")
        execute_query(self.db_connection,
                       """CREATE TABLE IF NOT EXISTS data (
                                    key TEXT PRIMARY KEY,
                                    dtype,
                                    data_clocks TEXT,
                                    last_writer TEXT,
                                    data
                                );
                            """
        )
    # Put raw data into memory
    def put(self, key, data, causal_metadata, last_writer, persist=True):
        self.data[key] = data
        self.data_clocks[key] = causal_metadata
        self.last_writer[key] = last_writer
        if persist:
            self._persist_data(key)

    # Get data for a given key
    def get(self, key, check_disk=True):
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
        # returns a tuple in format (key, data, data_clocks, last_writer)
        query_result = execute_read_query(self.db_connection, f"SELECT * FROM data WHERE key='{key}'")
        if not query_result:
            return None
        query_result = query_result[0]
        # Put the newly retrieved data into memory
        data = dict(val=dict(data=query_result[4], dtype=query_result[1]),
                    clock=json.loads(query_result[2]),
                    last_writer=json.loads(query_result[3]))
        self.put(query_result[0], data['val'], data['clock'], data['last_writer'], persist=False)
        return data
    
    # Write all available data from memory to disk
    def _persist_all_data(self):
        data_tuples = [(key, self.data[key]["dtype"], json.dumps(self.data_clocks[key]), json.dumps(self.last_writer[key]), self.data[key]["data"]) for key in self.data.keys()]
        if data_tuples:
            for t in data_tuples:
                # INSERT query
                execute_query(self.db_connection,
                                """
                                    REPLACE INTO
                                    data (key, dtype, data_clocks, last_writer, data)
                                    VALUES (?, ?, ?, ?, ?);
                                """, t)
                
    # Write data for a given key from memory to disk
    def _persist_data(self, key):
        data_tuple = (key, self.data[key]["dtype"], json.dumps(self.data_clocks[key]), json.dumps(self.last_writer[key]), self.data[key]["data"])
        # INSERT query
        print(len(data_tuple[-1]))
        execute_query(self.db_connection,
                        """
                            REPLACE INTO
                            data (key, dtype, data_clocks, last_writer, data)
                            VALUES (?, ?, ?, ?, ?);
                        """, data_tuple)
        
    # Retrieve all available keys
    def get_keys(self):
        query_result = execute_read_query(self.db_connection, f"SELECT DISTINCT(key) FROM data")
        if not query_result:
            return []
        query_result = [i[0] for i in query_result]
        return query_result
    
    # Cache causal-metadata for a given key into memory
    # returns data_clock and last writer
    def cache_causal_metadata(self, key):
        if key in self.data_clocks:
            return self.data_clocks[key]
        # returns a tuple in format (key, data, data_clocks, last_writer)
        query_result = execute_read_query(self.db_connection, f"SELECT data_clocks, last_writer FROM data WHERE key='{key}'")
        if not query_result:
            return [None, None]
        query_result = query_result[0]
        # Put the newly retrieved data into memory
        clock = json.loads(query_result[0])
        last_writer = json.dumps(query_result[1])
        return clock, last_writer
    
    """ Generate data partitions and assign them to shards
    * Returns a dict(shard_id: binary_data)
    * binary_data encodes 2 pieces of information: 1. idx: position of that partition in the entire binary string
                                                   2. len: length of the partition
      both attributes are prepended to each binary string partition.
      Additionally for both idx and len we store the number a value for the number of bytes used to express that metadata (1 byte max)
      Ex: data_partition = b'0123' -> resulting_partition = b'10140123', where [1] is the index and [3] is the length of the string
                                                                         [0] and [2] are single bytes defining the length of metadata
    * Why do we need to keep track of lenght?
      When generating destination shard_id's, 2 different partions might land on the same shard
      To avoid duplicating keys on that shard, we concatenate 2 partitions into 1 and store it with helpful decomposition metadata.
    * Assuming prepended metadata (each piece, both idx and len) will not exceed 256 bytes.
      Meaning we will not account for idx and len values above 2^256. 

    Hashing explained:
        We need a deterministic approach for hashing keys to generate multiple destination nodes (shards) 
        1. We generate the first hash by hashing the original key
        2. Every consequtive hash will be generated by appending a counter 0,1,2... to the previously used key
        Ex. key = "apple", num_partitions = 3
            dest_shard1 = hash("apple") % num_shards
            dest_shard2 = hash("apple0") % num_shards
            dest_shard3 = hash("apple01") % num_shards
    """
    def prepare_data_partitions_hashing(self, key, data, num_partitions, total_shards, shard_id):
        # Determine the number of bytes needed for storing metadata (each result must fit in 1 byte)
        idx_bytes = 1 if num_partitions < 256 else math.ceil(math.log(num_partitions, 256))
        len_bytes = 1 if len(data) < 256 else math.ceil(math.log(len(data), 256))
        # If the length of binary string is less than num_partitions, we will just store data locally in one piece
        if len(data) < num_partitions:
            idx_bstr = int(1).to_bytes(1, 'big') + int(0).to_bytes(1, 'big')
            len_bstr = len_bytes.to_bytes(1, 'big') + len(data).to_bytes(len_bytes, 'big')
            return {shard_id: idx_bstr+len_bstr+data}
        # Otherwise partition data into num_partitions pieces
        # if cannot partition evenly, last partition gets the smallest piece
        partitions = dict()
        step = (len(data) + num_partitions - 1) // num_partitions  # ceiling
        start = 0
        end = start + step
        hash = hashlib.sha256()  # hash function used to generate destination shard
        counter = 0
        while end < len(data):
            # Generate destination shard
            hash.update(key.encode())
            id = int.from_bytes(hash.digest(), 'big') % total_shards
            if not id in partitions:
                partitions[id] = b''
            # Generate a partition.
            # The partition index is prepended to the front of bytes string
            idx_bstr = idx_bytes.to_bytes(1, 'big') + counter.to_bytes(idx_bytes, 'big')
            len_bstr = len_bytes.to_bytes(1, 'big') + (end-start).to_bytes(len_bytes, 'big')
            partitions[id] += idx_bstr + len_bstr + data[start:end]
            # Update iterators
            key += str(counter)
            counter += 1
            start += step
            end += step
        # Cleanup the final partition
        end = len(data)
        hash.update(key.encode())
        id = int.from_bytes(hash.digest(), 'big') % total_shards
        if not id in partitions:
                partitions[id] = b''
        # Generate a partition.
        # The partition index is prepended to the front of bytes string
        idx_bstr = idx_bytes.to_bytes(1, 'big') + counter.to_bytes(idx_bytes, 'big')
        len_bstr = len_bytes.to_bytes(1, 'big') + (end-start).to_bytes(len_bytes, 'big')
        partitions[id] += idx_bstr + len_bstr + data[start:end]
        return partitions
    
    # Generate data partitions and assign them to all available shards on the network
    # This approach will spread all data across the entire network
    def prepare_data_partitions(self, data, total_shards):
        # If the length of binary string is less than total_shards, we send 1 byte partitions to first len(data) shards
        # Since retrieving data requires snooping the entire network, we do need need determinism in figuring out exact shards
        num_partitions = total_shards if len(data) >= total_shards else len(data)
        # Determine the number of bytes needed for storing metadata
        idx_bytes = 1 if num_partitions < 256 else math.ceil(math.log(num_partitions, 256))

        # Partition data into num_partitions pieces
        # if cannot partition evenly, last partition gets the smallest piece
        partitions = dict()
        step = (len(data) + num_partitions - 1) // num_partitions  # ceiling
        start = 0
        end = start + step
        id = 0
        while end < len(data):
            # Generate a partition.
            # The partition index is prepended to the front of bytes string
            idx_bstr = idx_bytes.to_bytes(1, 'big') + id.to_bytes(idx_bytes, 'big')
            partitions[id] = idx_bstr + data[start:end]
            # Update iterators
            id += 1
            start += step
            end += step
        # Cleanup the final partition
        end = len(data)
        # Generate a partition.
        # The partition index is prepended to the front of bytes string
        idx_bstr = idx_bytes.to_bytes(1, 'big') + id.to_bytes(idx_bytes, 'big')
        partitions[id] = idx_bstr + data[start:end]
        return partitions
    
    # Recompose hashed key data partitions
    # partitions: list of binary strings (which can be recomposed into a single binary string)
    #             it is the responsibility of the client to retrieve correct partitons
    def compose_data_from_partitions_hash(self, partitions):
        # Organize data orderigns in a dict
        orderings = dict()
        max_idx = 0
        for p in partitions:
            while len(p) > 0:
                idx_num_bytes = int.from_bytes(p[:1], 'big')
                index_byte = int.from_bytes(p[1:1+idx_num_bytes], 'big')
                p = p[1+idx_num_bytes:]
                len_num_bytes = int.from_bytes(p[:1], 'big')
                len_byte = int.from_bytes(p[1:1+len_num_bytes], 'big')
                p = p[1+len_num_bytes:]
                if index_byte > max_idx:
                    max_idx = index_byte
                orderings[index_byte] = p[:len_byte]
                p = p[len_byte:]
        # Recompose the data
        data = b''
        for i in range(max_idx+1):
            p = orderings.get(i, None)
            if p == None:
                # We got invalid input - missing a partition
                return None
            data += p
        return data
    
    # Recompose data partitions
    # partitions: list of binary strings (which can be recomposed into a single binary string)
    #             it is the responsibility of the client to retrieve correct partitons
    def compose_data_from_partitions(self, partitions):
        # Organize data orderigns in a dict
        orderings = dict()
        max_idx = 0
        for p in partitions:
            idx_num_bytes = int.from_bytes(p[:1], 'big')
            index_byte = int.from_bytes(p[1:1+idx_num_bytes], 'big')
            if index_byte > max_idx:
                    max_idx = index_byte
            p = p[1+idx_num_bytes:]
            orderings[index_byte] = p
                
        # Recompose the data
        data = b''
        for i in range(max_idx+1):
            p = orderings.get(i, None)
            if p == None:
                # We got invalid input - missing a partition
                return None
            data += p
        return data
