import os, json
from flask import jsonify
import concurrent.futures
import time
from multiprocessing.pool import ThreadPool
import sqlite3
from sqlite3 import Error
from threading import Lock

from clocks import new_clock
from utils import RepeatedTimer


# define
DATA_PATH = os.path.dirname(__file__) + "/.metadata/"
DATA_ENCODING = "iso-8859-1"
DATA_PERSISTANCE_PERIODICITY = 1  # in seconds
LOCK = Lock()

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
# SQLite database functionality

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path, check_same_thread=False)
    except Error as e:
        raise e
    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("YES")
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
        self.timer = RepeatedTimer(DATA_PERSISTANCE_PERIODICITY, self._persist_all_data)
        # Set up SQL database
        self.db_connection = create_connection(DATA_PATH+"data_storage.db")
        execute_query(self.db_connection,
                       """CREATE TABLE IF NOT EXISTS data (
                                    
                                    key TEXT PRIMARY KEY,
                                    data BINARY,
                                    data_clocks TEXT,
                                    last_writer TEXT
                                );
                            """
        )
    # Put raw data into memory
    def put(self, key, data, causal_metadata, last_writer):
        self.data[key] = data
        self.data_clocks[key] = causal_metadata
        self.last_writer[key] = last_writer

    # Get data for a given key
    def get(self, key, check_disk=True):
        # Check if data is stored in memory (most up-to date copy)
        if key in self.data:
            return dict(
                val=self.data[key].encode(DATA_ENCODING),
                clock=self.data_clocks[key],
                last_writer=self.last_writer[key]
                )
        # Otherwise check on disk
        elif check_disk:
            return self._get_from_disk(key)

    # Search and get data from disk for a given key
    def _get_from_disk(self, key):
        # returns a tuple in format (key, data, data_clocks, last_writer)
        query_result = execute_read_query(self.db_connection, f"SELECT * FROM data WHERE key='{key}'")[0]
        # Put the newly retrieved data into memory
        data = dict(val=query_result[1],
                    clock=json.loads(query_result[2]),
                    last_writer=json.loads(query_result[3]))
        self.put(query_result[1], data['val'], data['clock'], data['last_writer'])
        return data
    
    # Write all available data from memory to disk
    def _persist_all_data(self):
        data_tuples = [str((key, self.data[key], json.dumps(self.data_clocks[key]), json.dumps(self.last_writer[key]))) for key in self.data.keys()]
        if data_tuples:
            # INSERT query
            execute_query(self.db_connection,
                            """
                                REPLACE INTO
                                data (key, data, data_clocks, last_writer)
                                VALUES
                                {};
                            """.format(",".join(data_tuples))
            )

    # Retrieve data stored locally and put it onto the network
    def prepare_put_binary_data(self, key, file_path):
        with open(file_path, 'rb') as file:
            data = file.read()
            self.data[key] = data
            self.data_clocks[key] = new_clock(1)
            self.last_writer[key] = self.owner
